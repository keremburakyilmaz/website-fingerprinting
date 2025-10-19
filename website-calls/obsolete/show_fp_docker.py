#!/usr/bin/env python3
"""
Features:
- Open a target URL in a chosen browser: chromium|chrome|brave|firefox|tor
- (Tor support is best-effort; Tor Browser intentionally resists automation.)
- Dump the first 2000 chars of body innerText.
- Optionally write JSON result to an output file.
- Exit code 0 on success, 3 when fingerprint JSON not found, 1 on other errors.

Example usages:
  python3 website-calls/show_fp.py --browser chrome --url http://localhost:80
  python3 website-calls/show_fp.py --browser firefox --url http://localhost:80 --wait 4000 -o out.json
  python3 website-calls/show_fp.py --browser tor --url http://localhost:80

Tor Browser Notes (macOS paths assumed):
- Point Selenium's Firefox binary to Tor Browser's internal Firefox build
- This may fail if Tor Browser updates or its directory layout changes
- Advanced: you may need to enable Marionette (automation) or use a dedicated profile; this script attempts a minimal approach.

Dependencies:
  pip install -r requirements.txt

"""
from __future__ import annotations
import argparse
import sys
import tempfile
import shutil
from pathlib import Path
from typing import Optional, List


from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService


# Pinned binary & driver paths baked in Docker image

# Chrome-for-testing binary location (after Dockerfile unzip/mv)
BINARIES = {
    "chrome": "/usr/local/bin/google-chrome",
    "brave": "/usr/bin/brave-browser",
    "firefox": "/usr/local/bin/firefox",
}

CHROMEDRIVER_PATH = "/usr/local/bin/chromedriver"
GECKODRIVER_PATH = "/usr/local/bin/geckodriver"

def detect_path(p: str) -> Optional[str]:
    return p if Path(p).exists() else None


def build_driver(browser: str, headless: bool, privacy_max: bool = False, incognito: bool = False, extensions: Optional[List[str]] = None) -> webdriver.Remote:

    b = browser.lower()
    exts = extensions or []
    if b in {"chrome", "brave"}:
        from selenium.webdriver.chrome.options import Options as ChromeOptions
        options = ChromeOptions()
        import os
        user_dir = tempfile.mkdtemp(prefix=f"{b}-profile-")
        print(f"[debug] Using user-data-dir: {user_dir}")
        print(f"[debug] Contents: {os.listdir(user_dir)}")
        print(f"[debug] Permissions: {oct(os.stat(user_dir).st_mode)} Owner: {os.stat(user_dir).st_uid}")
        print(f"[debug] Running as UID: {os.getuid()}")
        options.add_argument(f"--user-data-dir={user_dir}")
        options._temp_user_dir = user_dir  # Attach for later cleanup
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--remote-debugging-port=9222")
        if incognito:
            options.add_argument("--incognito")
        options.binary_location = BINARIES[b]
        if privacy_max:
            for flag in [
                "--disable-plugins-discovery","--disable-extensions","--disable-popup-blocking",
                "--disable-translate","--disable-background-networking","--disable-sync",
                "--disable-default-apps","--disable-webgl","--disable-site-isolation-trials"
            ]:
                options.add_argument(flag)
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option("useAutomationExtension", False)
        for ext in exts:
            if ext.endswith(".crx"):
                options.add_extension(ext)
        service = ChromeService(executable_path=CHROMEDRIVER_PATH)
        return webdriver.Chrome(service=service, options=options)

    if b in {"firefox", "tor"}:
        from selenium.webdriver.firefox.options import Options as FirefoxOptions
        options = FirefoxOptions()
        if headless:
            options.add_argument("-headless")
        if incognito:
            options.add_argument("-private")
        profile = webdriver.FirefoxProfile()
        if b == "tor":
            profile.set_preference("network.proxy.type", 1)
            profile.set_preference("network.proxy.socks", "127.0.0.1")
            profile.set_preference("network.proxy.socks_port", 9050)
            profile.set_preference("network.proxy.socks_remote_dns", True)
        if privacy_max:
            for k, v in [
                ("privacy.resistFingerprinting", True),
                ("privacy.trackingprotection.enabled", True),
                ("privacy.trackingprotection.fingerprinting.enabled", True),
                ("privacy.trackingprotection.cryptomining.enabled", True),
                ("privacy.firstparty.isolate", True),
                ("webgl.disabled", True),
                ("dom.webnotifications.enabled", False),
                ("dom.webnotifications.serviceworker.enabled", False),
                ("dom.push.enabled", False),
                ("dom.battery.enabled", False),
                ("dom.enable_performance", False),
                ("media.peerconnection.enabled", False),
                ("media.navigator.enabled", False),
                ("media.webspeech.recognition.enable", False),
                ("media.webspeech.synth.enabled", False),
                ("beacon.enabled", False),
                ("geo.enabled", False),
                ("network.cookie.cookieBehavior", 1),
                ("network.dns.disablePrefetch", True),
                ("network.prefetch-next", False),
                ("network.http.sendRefererHeader", 0),
                ("network.http.referer.spoofSource", True),
                ("network.http.referer.XOriginPolicy", 2),
                ("network.http.referer.XOriginTrimmingPolicy", 2),
            ]:
                profile.set_preference(k, v)
        for ext in exts:
            if ext.endswith(".xpi"):
                profile.add_extension(ext)
        profile.update_preferences()
        service = FirefoxService(executable_path=GECKODRIVER_PATH)
        return webdriver.Firefox(service=service, options=options, firefox_profile=profile)

    raise ValueError(f"Unsupported browser: {browser}")



def dump_body(driver, limit: int = 10000) -> str:
    try:
        text = driver.execute_script("return document.body ? (document.body.innerText || '') : '';")
        return text[:limit]
    except WebDriverException:
        return "<unable to retrieve body text>"


def parse_args():
    p = argparse.ArgumentParser(description="Fetch fingerprint JSON from a page using Selenium")
    p.add_argument("--browser", required=True, choices=["chromium", "chrome", "brave", "firefox", "tor"], help="Browser to use")
    p.add_argument("--url", required=True, help="Target URL")
    p.add_argument("--wait", type=int, default=10000, help="Wait ms for window.__FP_RESULT__ before fallback (default 2000)")
    p.add_argument("-o", "--out", help="Output JSON file path")
    p.add_argument("--headless", action="store_true", help="Run browser headless (may change fingerprint)")
    p.add_argument("--privacy-max", action="store_true", help="Enable all available privacy settings/extensions")
    p.add_argument("--incognito", action="store_true", help="Enable incognito/private mode")
    p.add_argument("--extension", action="append", help="Path to browser extension (.crx or .xpi). Can be repeated.")
    return p.parse_args()


def main():
    args = parse_args()
    browser = args.browser
    url = args.url
    wait_ms = args.wait
    out_path = Path(args.out).resolve() if args.out else None
    privacy_max = args.privacy_max
    incognito = args.incognito
    extensions = args.extension or []

    print(f"[config] Browser: {browser}")
    print(f"[config] Privacy-max: {privacy_max}")
    print(f"[config] Incognito/private: {incognito}")
    print(f"[config] Extensions: {extensions}")

    driver = None
    temp_user_dir = None
    try:
        print(f"[info] Launching {browser} ...")
        driver = build_driver(browser, headless=args.headless)
        # If Chrome/Brave, remember temp user dir for cleanup
        if hasattr(driver, 'options') and hasattr(driver.options, '_temp_user_dir'):
            temp_user_dir = driver.options._temp_user_dir
        print(f"[info] Navigating to {url} ...")
        driver.get(url)

        snippet = dump_body(driver)
        print("---------------- BODY (truncated) ----------------")
        print(snippet)
        print("---------------- END BODY ----------------")
        sys.exit(3)
    except KeyboardInterrupt:
        print("[info] Interrupted by user.")
        sys.exit(130)
    except Exception as e:
        print(f"[error] {e.__class__.__name__}: {e}")
        if browser == "tor":
            print("[hint] Tor automation is fragile. If this keeps failing: \n"
                  " - Ensure Tor Browser is fully installed and opened at least once.\n"
                  " - Disable 'Safest' security level (try 'Standard' or 'Safer').\n"
                  " - Close normally running Tor Browser instance before automation.\n"
                  " - Consider using plain Firefox with a Tor SOCKS proxy for stable automation.")
        sys.exit(1)
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass
        if temp_user_dir:
            try:
                shutil.rmtree(temp_user_dir)
            except Exception:
                pass


if __name__ == "__main__":
    main()
