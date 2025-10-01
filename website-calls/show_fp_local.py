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
import json
import sys
import time
from pathlib import Path
from typing import Optional

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException

# Default macOS application paths; adjust as needed for your system.
MAC_PATHS = {
    "chrome": "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "brave": "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    "chromium": "/Applications/Chromium.app/Contents/MacOS/Chromium",
    # Tor outer stub binary usually exists at this path, but we often need the inner Firefox binary.
    "tor_binary": "/Applications/Tor Browser.app/Contents/MacOS/firefox",
    # Alternate inner path (older bundles):
    "tor_alt": "/Applications/Tor Browser.app/Contents/Resources/TorBrowser/Tor/Browser/firefox",
}

TOR_PROFILE_CANDIDATES = [
    "/Applications/Tor Browser.app/Contents/Resources/TorBrowser/Tor/Browser/TorBrowser/Data/Browser/profile.default",
]
# detect if a given binary path ecists
def detect_path(p: str) -> Optional[str]:
    return p if Path(p).exists() else None


def build_driver(browser: str, headless: bool, privacy_max: bool = False, incognito: bool = False, extensions: list = None) -> webdriver.Remote:
    b = browser.lower()
    extensions = extensions or []

    if b in {"chrome", "brave", "chromium"}:
        from selenium.webdriver.chrome.options import Options as ChromeOptions
        options = ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
        if incognito:
            options.add_argument("--incognito")
        if b != "chrome":
            target_key = b
            binary = detect_path(MAC_PATHS.get(target_key, ""))
            if binary:
                options.binary_location = binary
            else:
                print(f"[warn] Could not find {b} binary at expected path; falling back to system Chrome.")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        # options.add_argument("--disable-gpu")
        if privacy_max:
            # Prevents Chrome from scanning for and loading system-wide plugins (like Flash, PDF readers, etc.).  
            # This reduces the fingerprinting surface because fewer plugins are exposed via JS APIs like navigator.plugins. 
            options.add_argument("--disable-plugins-discovery")

            # Disables all installed extensions.  
            # Extensions can leak identifying information (IDs, web-accessible resources) that make you trackable.
            options.add_argument("--disable-extensions")

            # Turns off popup blocking.  
            # It only ensures automation doesn't break when sites trigger popups  
            # It doesn’t increase privacy — arguably the opposite.  
            options.add_argument("--disable-popup-blocking")

            # It only ensures automation doesn't break when sites trigger popups 
            # It doesn’t increase privacy — arguably the opposite
            options.add_argument("--disable-translate")

            # Prevents Chrome from making background connections (e.g., to Google update checks, safe browsing, metrics).  
            # Helps privacy by reducing "phone home" traffic.  
            options.add_argument("--disable-background-networking")

            # Disables Chrome Sync (with a Google account).  
            # Prevents personal data (history, bookmarks, passwords) from syncing to Google. 
            options.add_argument("--disable-sync")

            # Stops Chrome from installing or running default bundled apps (like Docs, YouTube app)
            # Reduces background activity and identifiable behavior. 
            options.add_argument("--disable-default-apps")

            # Turns off WebGL (3D rendering in canvas).  
            # Major fingerprinting surface (GPU model, driver bugs, shader precision)
            # Disabling WebGL prevents websites from collecting unique GPU fingerprints
            options.add_argument("--disable-webgl")

            # Disables experimental site isolation.  
            # Normally, site isolation is a *security* feature, but it sometimes changes process allocation in ways detectable by fingerprinting            
            options.add_argument("--disable-site-isolation-trials")

            # Hides the "Chrome is being controlled by automated software" banner
            options.add_experimental_option("excludeSwitches", ["enable-automation"])

            # Prevents Chrome from loading the standard "automation extension" that Selenium injects
            # By default, Selenium adds a hidden extension to control the browser, which leaves detectable traces
            options.add_experimental_option("useAutomationExtension", False)

        for ext in extensions:
            if ext.endswith(".crx"):
                options.add_extension(ext)
        return webdriver.Chrome(options=options)

    if b == "firefox":
        from selenium.webdriver.firefox.options import Options as FirefoxOptions
        from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
        options = FirefoxOptions()
        if headless:
            options.add_argument("-headless")
        if incognito:
            options.add_argument("-private")
        profile = FirefoxProfile()
        if privacy_max:
            profile.set_preference("privacy.resistFingerprinting", True)
            profile.set_preference("privacy.trackingprotection.enabled", True)
            profile.set_preference("privacy.trackingprotection.fingerprinting.enabled", True)
            profile.set_preference("privacy.trackingprotection.cryptomining.enabled", True)
            profile.set_preference("privacy.firstparty.isolate", True)
            profile.set_preference("webgl.disabled", True)
            profile.set_preference("dom.webnotifications.enabled", False)
            profile.set_preference("dom.webnotifications.serviceworker.enabled", False)
            profile.set_preference("dom.push.enabled", False)
            profile.set_preference("dom.battery.enabled", False)
            profile.set_preference("dom.enable_performance", False)
            profile.set_preference("media.peerconnection.enabled", False)
            profile.set_preference("media.navigator.enabled", False)
            profile.set_preference("media.webspeech.recognition.enable", False)
            profile.set_preference("media.webspeech.synth.enabled", False)
            profile.set_preference("beacon.enabled", False)
            profile.set_preference("geo.enabled", False)
            profile.set_preference("network.cookie.cookieBehavior", 1)
            profile.set_preference("network.dns.disablePrefetch", True)
            profile.set_preference("network.prefetch-next", False)
            profile.set_preference("network.http.sendRefererHeader", 0)
            profile.set_preference("network.http.referer.spoofSource", True)
            profile.set_preference("network.http.referer.XOriginPolicy", 2)
            profile.set_preference("network.http.referer.XOriginTrimmingPolicy", 2)
        for ext in extensions:
            if ext.endswith(".xpi"):
                profile.add_extension(ext)
        profile.update_preferences()
        options.profile = profile
        return webdriver.Firefox(options=options)

    if b == "tor":
        from selenium.webdriver.firefox.options import Options as FirefoxOptions
        from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
        options = FirefoxOptions()
        if headless:
            options.add_argument("-headless")
        if incognito:
            options.add_argument("-private")
        tor_bin = detect_path(MAC_PATHS["tor_binary"]) or detect_path(MAC_PATHS["tor_alt"])
        if not tor_bin:
            raise FileNotFoundError("Tor Browser binary not found at expected macOS paths.")
        options.binary_location = tor_bin
        profile_path = next((p for p in TOR_PROFILE_CANDIDATES if Path(p).exists()), None)
        if profile_path:
            profile = FirefoxProfile(profile_path)
        else:
            profile = FirefoxProfile()
            profile.set_preference("network.proxy.type", 1)
            profile.set_preference("network.proxy.socks", "127.0.0.1")
            profile.set_preference("network.proxy.socks_port", 9050)
            profile.set_preference("network.proxy.socks_remote_dns", True)
        profile.set_preference("marionette.enabled", True)
        profile.set_preference("dom.webdriver.enabled", False)
        profile.set_preference("use_mozillapkix_verification", True)
        if privacy_max:
            profile.set_preference("privacy.resistFingerprinting", True)
            profile.set_preference("privacy.trackingprotection.enabled", True)
            profile.set_preference("privacy.trackingprotection.fingerprinting.enabled", True)
            profile.set_preference("privacy.trackingprotection.cryptomining.enabled", True)
            profile.set_preference("privacy.firstparty.isolate", True)
            profile.set_preference("webgl.disabled", True)
            profile.set_preference("dom.webnotifications.enabled", False)
            profile.set_preference("dom.webnotifications.serviceworker.enabled", False)
            profile.set_preference("dom.push.enabled", False)
            profile.set_preference("dom.battery.enabled", False)
            profile.set_preference("dom.enable_performance", False)
            profile.set_preference("media.peerconnection.enabled", False)
            profile.set_preference("media.navigator.enabled", False)
            profile.set_preference("media.webspeech.recognition.enable", False)
            profile.set_preference("media.webspeech.synth.enabled", False)
            profile.set_preference("beacon.enabled", False)
            profile.set_preference("geo.enabled", False)
            profile.set_preference("network.cookie.cookieBehavior", 1)
            profile.set_preference("network.dns.disablePrefetch", True)
            profile.set_preference("network.prefetch-next", False)
            profile.set_preference("network.http.sendRefererHeader", 0)
            profile.set_preference("network.http.referer.spoofSource", True)
            profile.set_preference("network.http.referer.XOriginPolicy", 2)
            profile.set_preference("network.http.referer.XOriginTrimmingPolicy", 2)
        for ext in extensions:
            if ext.endswith(".xpi"):
                profile.add_extension(ext)
        profile.update_preferences()
        options.profile = profile
        try:
            driver = webdriver.Firefox(options=options, service=webdriver.firefox.service.Service("/usr/local/bin/geckodriver"))
        except WebDriverException as e:
            raise RuntimeError("Failed to launch Tor Browser via Selenium. Tor may block automation.") from e
        return driver

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
    try:
        print(f"[info] Launching {browser} ...")
        # build_driver will be updated next
        driver = build_driver(browser, headless=args.headless)
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


if __name__ == "__main__":
    main()
