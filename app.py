"""Run the local SupeRR dashboard. No third-party packages required."""
import argparse
import functools
import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading
import webbrowser

ROOT = Path(__file__).resolve().parent


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            body = json.dumps({"status": "ok", "app": "SupeRR Selector"}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()

    def end_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8501)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()
    if not (ROOT / "web" / "data" / "dashboard.json").exists():
        print("Dashboard data is missing. Run: python -m analysis.build --data-dir data/raw")
        return 1
    try:
        server = ThreadingHTTPServer(("127.0.0.1", args.port), functools.partial(Handler, directory=str(ROOT / "web")))
    except OSError as error:
        print(f"Cannot start on port {args.port}: {error}\nTry: python app.py --port {args.port + 1}")
        return 1
    url = f"http://127.0.0.1:{args.port}"
    print(f"\nSupeRR Selector is ready: {url}\nPress Ctrl+C to stop.\n", flush=True)
    if not args.no_browser:
        threading.Timer(.5, webbrowser.open, args=(url,)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDashboard stopped.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
