"""Capture deck screenshots of the running app with Playwright + installed Edge."""
import sys
from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8765"
with sync_playwright() as p:
    b = p.chromium.launch(channel="msedge", headless=True)
    pg = b.new_page(viewport={"width": 1440, "height": 900}, device_scale_factor=2)
    pg.goto(BASE + "/"); pg.wait_for_timeout(1500)
    pg.screenshot(path="shots/landing.png")
    pg.goto(BASE + "/#integration"); pg.wait_for_timeout(800)
    pg.screenshot(path="shots/integration.png")
    for n in (2, 1, 5):
        pg.goto(f"{BASE}/app?sample={n}")
        pg.wait_for_selector(".verdict", timeout=120000); pg.wait_for_timeout(1500)
        pg.screenshot(path=f"shots/result{n}.png")
        pg.screenshot(path=f"shots/result{n}_full.png", full_page=True)
    pg.click("#tab-history"); pg.wait_for_timeout(1000)
    pg.screenshot(path="shots/queue.png")
    pg.goto(BASE + "/docs"); pg.wait_for_timeout(2500)
    pg.screenshot(path="shots/docs.png")
    b.close()
print("done")
