#!/usr/bin/env python3
"""
Features:
  - Open a target URL in a chosen browser: chrome|brave|firefox
  - Collect fingerprinting features and output as JSON (page_body.json)
  - Exit code 3 when fingerprint JSON not found, 1 on other errors.

Example usage:
    python3 show_fp_local.py --browser chrome --url http://localhost:80

Dependencies:
    pip install -r requirements.txt
"""

from __future__ import annotations
import argparse
import json
from bs4 import BeautifulSoup
import sys
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
    "firefox": "/Applications/Firefox.app/Contents/MacOS/firefox",
}

def detect_path(p: str) -> Optional[str]:
    """Return path if it exists, else None."""
    return p if Path(p).exists() else None

def build_driver(browser: str, headless: bool, privacy_max: bool = False, incognito: bool = False, extensions: list = None) -> webdriver.Remote:
    """Build a Selenium WebDriver for the specified browser and options."""
    b = browser.lower()
    extensions = extensions or []

    if b == "chrome":
        from selenium.webdriver.chrome.options import Options as ChromeOptions
        options = ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
        if incognito:
            options.add_argument("--incognito")
        # Chrome-specific privacy settings
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        if privacy_max:
            # Maximum privacy flags
            options.add_argument("--disable-plugins-discovery")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-popup-blocking")
            options.add_argument("--disable-translate")
            options.add_argument("--disable-background-networking")
            options.add_argument("--disable-sync")
            options.add_argument("--disable-default-apps")
            options.add_argument("--disable-webgl")
            options.add_argument("--disable-site-isolation-trials")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option("useAutomationExtension", False)
            options.add_argument("--enable-features=EnableDoNotTrack")
            options.add_argument("--force-enable-do-not-track")
            options.add_argument("--disable-third-party-cookies")
            options.add_argument("--disable-features=InterestCohortAPI,Topics,FirstPartySets,PrivacySandboxSettings2")
        else:
            # Minimal fingerprint protection
            options.add_argument("--disable-plugins-discovery")
            options.add_argument("--disable-popup-blocking")
            options.add_argument("--enable-features=EnableDoNotTrack")
        for ext in extensions:
            if ext.endswith(".crx"):
                options.add_extension(ext)
        return webdriver.Chrome(options=options)

    if b == "brave":
        from selenium.webdriver.chrome.options import Options as ChromeOptions
        options = ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
        if incognito:
            options.add_argument("--incognito")
        binary = detect_path(MAC_PATHS.get("brave", ""))
        if binary:
            options.binary_location = binary
        else:
            print(f"[warn] Could not find Brave binary at expected path; falling back to system Chrome.")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        if privacy_max:
            options.add_argument("--disable-plugins-discovery")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-popup-blocking")
            options.add_argument("--disable-translate")
            options.add_argument("--disable-background-networking")
            options.add_argument("--disable-sync")
            options.add_argument("--disable-default-apps")
            options.add_argument("--disable-webgl")
            options.add_argument("--disable-site-isolation-trials")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option("useAutomationExtension", False)
        else:
            options.add_argument("--disable-plugins-discovery")
            options.add_argument("--disable-popup-blocking")
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
            # Maximum privacy/anti-fingerprinting settings
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
            # Additional privacy settings
            profile.set_preference("device.sensors.enabled", False)
            profile.set_preference("device.sensors.ambientLight.enabled", False)
            profile.set_preference("device.sensors.motion.enabled", False)
            profile.set_preference("device.sensors.orientation.enabled", False)
            profile.set_preference("device.sensors.proximity.enabled", False)
            profile.set_preference("dom.gamepad.enabled", False)
            profile.set_preference("dom.w3c_pointer_events.enabled", False)
            profile.set_preference("dom.event.clipboardevents.enabled", False)
            profile.set_preference("layers.acceleration.disabled", True)
            profile.set_preference("dom.serviceWorkers.enabled", False)
            profile.set_preference("dom.storage.enabled", False)
            profile.set_preference("dom.sessionstore.enabled", False)
            profile.set_preference("dom.indexedDB.enabled", False)
            profile.set_preference("dom.caches.enabled", False)
            profile.set_preference("browser.cache.disk.enable", False)
            profile.set_preference("browser.cache.memory.enable", False)
        else:
            # Minimal fingerprint protection
            profile.set_preference("privacy.trackingprotection.enabled", True)
            profile.set_preference("privacy.trackingprotection.fingerprinting.enabled", True)
            profile.set_preference("privacy.trackingprotection.cryptomining.enabled", True)
        for ext in extensions:
            if ext.endswith(".xpi"):
                profile.add_extension(ext)
        profile.update_preferences()
        options.profile = profile
        return webdriver.Firefox(options=options)

    # Tor support removed
    raise ValueError(f"Unsupported browser: {browser}")

def dump_body(driver) -> str:
    """Return the text content of the page body."""
    try:
        text = driver.execute_script(
            "return document.body ? (document.body.innerText || '') : '';"
        )
        return text
    except WebDriverException:
        return "<unable to retrieve body text>"

def parse_args():
    """Parse command-line arguments."""
    p = argparse.ArgumentParser(
        description="Fetch fingerprint JSON from a page using Selenium"
    )
    p.add_argument(
        "--browser",
        required=True,
        choices=["chromium", "chrome", "brave", "firefox"],
        help="Browser to use (chromium is an alias for chrome)"
    )
    p.add_argument("--url", required=True, help="Target URL")
    p.add_argument(
        "--headless",
        action="store_true",
        help="Run browser headless (may change fingerprint)"
    )
    p.add_argument(
        "--privacy-max",
        action="store_true",
        help="Enable all available privacy settings/extensions"
    )
    p.add_argument(
        "--incognito",
        action="store_true",
        help="Enable incognito/private mode"
    )
    p.add_argument(
        "--extension",
        action="append",
        help="Path to browser extension (.crx or .xpi). Can be repeated."
    )
    return p.parse_args()

def main():
    args = parse_args()
    browser = args.browser
    import random
    import time as _time
    url = args.url
    # Add cache-busting query parameter
    cache_buster = f"nocache={int(_time.time()*1000)}_{random.randint(0,99999)}"
    if "?" in url:
        url = url + "&" + cache_buster
    else:
        url = url + "?" + cache_buster
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
        driver = build_driver(
            browser,
            headless=args.headless,
            privacy_max=privacy_max,
            incognito=incognito,
            extensions=extensions
        )
        print(f"[info] Navigating to {url} ...")
        driver.get(url)

        # snippet = dump_body(driver)

        # Wait for the feature list to be populated (up to 5 seconds)
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        try:
            WebDriverWait(driver, 5).until(
                lambda d: d.find_elements(By.CSS_SELECTOR, "#featureList li")
            )
        except Exception:
            pass

        # Extract features from the rendered list
        features = {}
        for li in driver.find_elements(By.CSS_SELECTOR, "#featureList li"):
            try:
                key = li.find_element(By.TAG_NAME, "h3").text.strip()
                val = li.find_element(By.TAG_NAME, "pre").text.strip()
                features[key] = val
            except Exception:
                continue

        # List of all expected fingerprinting fields (update as needed)
        expected_fields = [
            "Canvas Fingerprint", "WebGL Vendor", "WebGL Renderer", "WebGL Shader Precision", "Detected Fonts", "User-Agent",
            "Screen Resolution", "Device Pixel Ratio", "Color Depth", "Time Zone", "Locale", "Platform", "CPU Cores", "Device Memory (GB)",
            "Multi-Monitor Position", "Media Devices", "WebRTC Candidate", "Cookies Enabled", "Accept-Language", "Do Not Track", "Plugins",
            "Audio Fingerprint", "WASM Compile Time (ms)", "TLS / JA3", "SNI / DNS / Cert Info", "Device Motion", "Device Orientation",
            "Mouse Sample", "Key Press Sample", "Scroll Sample", "Touch Gestures Sample"
        ]
        # Fill missing fields with empty string or default value
        for field in expected_fields:
            if field not in features:
                features[field] = ""

        # Output structured JSON
        import datetime
        output = {
            "timestamp": datetime.datetime.now().isoformat(),
            "title": driver.title,
            "features": {k: features[k] for k in expected_fields}
        }
        with open("page_body.json", "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        sys.exit(3)
    except KeyboardInterrupt:
        print("[info] Interrupted by user.")
        sys.exit(130)
    except Exception as e:
        print(f"[error] {e.__class__.__name__}: {e}")
        sys.exit(1)
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass

if __name__ == "__main__":
    main()