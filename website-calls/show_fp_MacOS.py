#!/usr/bin/env python3
"""
Features:
    - Open a target URL in a chosen browser: chrome|brave|firefox
    - Collect fingerprinting features and output as JSON (page_body.json)
    - Output a second config JSON (call_config.json) with run settings

Example usage:
        python3 show_fp_MacOS.py --browser chrome --url http://localhost:80
        python3 show_fp_MacOS.py --browser brave --url http://localhost:80 --incognito --privacy-max
        python3 show_fp_MacOS.py --browser firefox --url http://localhost:80 --extension ./extensions/firefox-xpi/ublock_origin-1.66.4.xpi --extension ./extensions/firefox-xpi/privacy-badger-latest.xpi --extension ./extensions/firefox-xpi/canvasblocker-1.11.xpi --extension ./extensions/firefox-xpi/noscript-13.0.9.xpi  --incognito
        python3 show_fp_MacOS.py --browser chrome --url http://localhost:80 --extension ./extensions/chromium-crx/ublock_origin_lite.crx --extension ./extensions/chromium-crx/privacy-badger-chrome.crx --extension ./extensions/chromium-crx/NoScript.crx  --incognito
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
        options.add_argument("--disable-features=DisableLoadExtensionCommandLineSwitch")

        if privacy_max:
            # Chrome "privacy_max" arguments
            # Based primarily on Chromium switch list (https://peter.sh/experiments/chromium-command-line-switches/) and
            # hardening recommendations for reducing fingerprinting surfaces.

            #Core anti-fingerprinting & UI isolation
            options.add_argument("--disable-plugins-discovery")  # Prevent Chrome from scanning system for installed plugins (flash, etc.)
            #options.add_argument("--disable-extensions")        # Disable extensions (they leak entropy, though some anti-FP ones may help)
            options.add_argument("--disable-popup-blocking")     # Avoid heuristic popup handling that can change behavior
            options.add_argument("--disable-translate")          # Disable Google Translate integration (contacts remote service)
            options.add_argument("--disable-site-isolation-trials")  # Avoid Site Isolation trials (reduce internal variation)
            options.add_argument("--disable-default-apps")       # Prevent bundled Chrome apps being installed
            options.add_experimental_option("excludeSwitches", ["enable-automation"])  # Remove Selenium "controlled by automated test software" flag
            options.add_experimental_option("useAutomationExtension", False)           # Don't load the automation extension (reduces detectability)
            options.add_argument("--force-enable-do-not-track")  # Explicitly enable Do Not Track
            options.add_argument("--enable-features=EnableDoNotTrack")

            #Privacy Sandbox & tracking APIs
            options.add_argument("--disable-third-party-cookies")  # Block all 3rd-party cookies (anti-tracking)
            options.add_argument("--disable-features=InterestCohortAPI,Topics,FirstPartySets,PrivacySandboxSettings2")  
            # Disables FLoC / Topics / Privacy Sandbox APIs (prevent cross-site profiling) 

            # Rendering & GPU fingerprinting
            options.add_argument("--disable-webgl")                # Disables WebGL (major high-entropy fingerprinting surface)
            options.add_argument("--disable-3d-apis")              # Disable all 3D rendering APIs (WebGL, WebGPU)
            options.add_argument("--disable-accelerated-2d-canvas")# Prevent hardware acceleration in 2D canvas (timing-based FP)
            options.add_argument("--disable-accelerated-video-decode")  # Disable video decoding via GPU
            options.add_argument("--disable-accelerated-video-encode")  # Disable video encoding via GPU
            options.add_argument("--disable-accelerated-mjpeg-decode")  # Disable MJPEG decode acceleration
            options.add_argument("--disable-angle-features")       # Disable ANGLE (WebGL rendering layer)
            options.add_argument("--disable-2d-canvas-clip-aa")    # Remove anti-alias differences (microvisual FP consistency)
            options.add_argument("--disable-smooth-scrolling")     # Reduce motion-based variations (UI rendering)
            options.add_argument("--disable-touch-drag-drop")      # Avoid touch event path fingerprinting
            options.add_argument("--disable-backing-store-limit")  # Simplify GPU memory heuristics

            #Media, Audio & Sensors
            options.add_argument("--disable-audio-output")         # Disable audio output (avoid probing audio stack)
            options.add_argument("--mute-audio")                   # Ensure no sound playback (audio fingerprinting)
            options.add_argument("--disable-speech-api")           # Disable Speech Recognition/Synthesis API
            options.add_argument("--disable-gamepad")              # Block Gamepad API (device enumeration surface)
            options.add_argument("--disable-media-session-api")    # Disable Media Session API (metadata leaks)
            options.add_argument("--disable-permissions-api")      # Prevent site querying permissions (microphone, camera state)

            #Networking, Sync, Telemetry
            options.add_argument("--disable-background-networking") # Disable all background fetches, experiments, update pings
            options.add_argument("--disable-sync")                  # Disable Chrome Sync with Google account
            options.add_argument("--use-mock-keychain")             # Dont use system keychain (prevents local identifiers)
            options.add_argument("--disable-logging")               # Suppress Chrome logs (avoid diagnostic info)
            #options.add_argument("--no-sandbox")                   # (Optional) run without sandbox; not privacy, only containerization

            # Optional: additional network isolation
            options.add_argument("--no-pings")                     # Disable hyperlink auditing (ping=)
            options.add_argument("--disable-preconnect")           # Disable speculative connections
            options.add_argument("--dns-prefetch-disable")         # Disable DNS prefetching
            options.add_argument("--disable-client-side-phishing-detection")  # Avoid Google SafeBrowsing pings
            options.add_argument("--safebrowsing-disable-auto-update")         # Prevent automatic SafeBrowsing DB updates
            options.add_argument("--disable-component-update")     # Prevent background component fetching (variations, CRL sets)
            options.add_argument("--disable-background-timer-throttling")      # Simplify timer behavior

            # Browser identity (could be set to arbitrary value --> Idea could be to 'fit into buckets' and display user-agent that is use by many people)
            options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0")  

            #Misc UI / debug
            options.add_argument("--disable-infobars")             # Hide “Chrome is being controlled by automated test software” banner
            options.add_argument("--hide-scrollbars")              # Reduce scroll metrics FP
            options.add_argument("--no-first-run")                 # Skip first-run dialogs
            options.add_argument("--no-default-browser-check")     # Skip default browser prompt
        for ext in extensions:
            if ext.endswith(".crx"):
                # options.add_argument('--load-extension={ext}')
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
            # Brave "privacy_max" arguments
            # Since Brave is a chromium-based browser, so settings/flags are similar to Chrome.
            # But: Brave is privacy based, many privacy features are already enabled by default.
            # Used sources are the Chromium switch list (https://peter.sh/experiments/chromium-command-line-switches/) (see above)

            # Core privacy & anti-fingerprinting (Brave baseline)
            options.add_argument("--disable-plugins-discovery")    # Prevent system plugin probing
            #options.add_argument("--disable-extensions")           # Disable all extensions; Brave already isolates them
            options.add_argument("--disable-popup-blocking")       # Avoid popup heuristics that change site flow
            options.add_argument("--disable-site-isolation-trials")# Remove experimental isolation variations
            options.add_argument("--disable-background-timer-throttling")  # Stabilize timing
            options.add_argument("--disable-accelerated-2d-canvas")# Avoid GPU timing variation
            options.add_argument("--disable-webgl")                # WebGL = fingerprinting vector
            options.add_argument("--disable-3d-apis")              # Disable all 3D APIs
            options.add_argument("--disable-gamepad")              # Prevent device enumeration
            options.add_argument("--disable-speech-api")           # Avoid speech synthesis FP
            options.add_argument("--mute-audio")                   # Block audio stack FP
            options.add_argument("--disable-audio-output")         # Disable audio probing
            
            #Disable Selenium automation detectability
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option("useAutomationExtension", False)

            #Optional: enforce stronger tracking & cookie policy
            options.add_argument("--disable-third-party-cookies")
            options.add_argument("--force-enable-do-not-track")

            #Network privacy (some Brave defaults, but reinforce)
            options.add_argument("--no-pings")
            options.add_argument("--disable-preconnect")
            options.add_argument("--dns-prefetch-disable")

            # Identity & consistency
            options.add_argument("--no-first-run")
            options.add_argument("--no-default-browser-check")
            options.add_argument("--disable-infobars")

            # Optional: spoof UA to generic (cross-browser comparability)
            options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:115.0) Gecko/20100101 Firefox/115.0")
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
            # arkenfox-inspired privacy_max prefs for Firefox
            # Source: arkenfox user.js (primary), Mozilla docs for resistFingerprinting and related prefs.
            # See: https://github.com/arkenfox/user.js and Firefox help pages.

            # Resist fingerprinting umbrella (enables many RFP behaviors)
            profile.set_preference("privacy.resistFingerprinting", True)          # Tor-like anti-fingerprinting behavior (timer, spoofing, APIs)

            # Timer and precision hardening (reduce high-resolution timers that help fingerprinting)
            profile.set_preference("privacy.resistFingerprinting.reduceTimerPrecision", True)
            # If you need to tune granularity: privacy.resistFingerprinting.reduceTimerPrecision.microseconds (see arkenfox notes)

            # Canvas / WebGL protections
            profile.set_preference("canvas.poisondata", True)                     # canvas hardening; blocks or randomizes canvas extraction
            profile.set_preference("privacy.resistFingerprinting.randomDataOnCanvasExtract", True)  # Randomize canvas readouts when RFP is enabled
            profile.set_preference("webgl.disabled", True)                       # Disable WebGL (major fingerprint surface).

            # Media / speech / audio / video: reduce surfaces
            profile.set_preference("media.peerconnection.enabled", False)         # Disable WebRTC by default (prevents local IP leaks)
            profile.set_preference("media.navigator.enabled", False)             # Block getUserMedia (camera/mic) enumeration.
            profile.set_preference("media.webspeech.recognition.enable", False)  # Disable WebSpeech recognition
            profile.set_preference("media.webspeech.synth.enabled", False)       # Disable WebSpeech synthesis
            profile.set_preference("dom.battery.enabled", False)                 # Disable battery API (timing/fingerprint leak)
            profile.set_preference("dom.gamepad.enabled", False)                 # Disable Gamepad API enumeration (fingerprint surface)

            # Sensors / motion / orientation
            profile.set_preference("device.sensors.enabled", False)
            profile.set_preference("device.sensors.motion.enabled", False)
            profile.set_preference("device.sensors.orientation.enabled", False)
            profile.set_preference("device.sensors.ambientLight.enabled", False)

            # Storage and persistence isolation
            profile.set_preference("dom.storage.enabled", False)                 # Disables localStorage (reduces storage-based tracking)
            profile.set_preference("dom.indexedDB.enabled", False)              # Disable IndexedDB
            profile.set_preference("dom.caches.enabled", False)                 # Disable Cache API
            profile.set_preference("dom.serviceWorkers.enabled", False)         # Disable Service Workers (used for tracking/persistence)
            profile.set_preference("browser.cache.disk.enable", False)          # Disable disk cache (less persistent evidence)
            profile.set_preference("browser.cache.memory.enable", False)

            # Network / privacy / referer / cookies
            profile.set_preference("network.dns.disablePrefetch", True)         # No DNS prefetch
            profile.set_preference("network.http.speculative-parallel-limit", 0) # No speculative connections
            profile.set_preference("network.prefetch-next", False)              # No link prefetch
            profile.set_preference("network.http.sendRefererHeader", 0)         # Don't send Referer header (0 = don't send)
            profile.set_preference("network.http.referer.spoofSource", True)
            profile.set_preference("network.cookie.cookieBehavior", 1)          # 1 = Block third-party cookies (0=accept all) – adjust if desired

            # Telemetry / telemetry-like network noise
            profile.set_preference("toolkit.telemetry.enabled", False)
            profile.set_preference("toolkit.telemetry.unified", False)
            profile.set_preference("datareporting.healthreport.uploadEnabled", False)
            profile.set_preference("browser.ping-centre.telemetry", False)
            profile.set_preference("dom.identity.enabled", False)

            # Safe-browsing / remote checks (disable to avoid "phone-home" network calls)
            profile.set_preference("browser.safebrowsing.enabled", False)
            profile.set_preference("browser.safebrowsing.malware.enabled", False)
            profile.set_preference("browser.safebrowsing.phishing.enabled", False)

            # Misc privacy & UI surfaces
            profile.set_preference("beacon.enabled", False)                      # navigator.sendBeacon disabled
            profile.set_preference("dom.push.enabled", False)                   # push notifications
            profile.set_preference("dom.webnotifications.enabled", False)
            profile.set_preference("dom.webnotifications.serviceworker.enabled", False)
            profile.set_preference("extensions.webextensions.remote", False)     # avoid remote ext processes (reduces extension surface)
            profile.set_preference("privacy.firstparty.isolate", True)          # Isolate storage by first-party (partitions)
            profile.set_preference("privacy.trackingprotection.enabled", True)  # Enable tracking protection lists
            profile.set_preference("privacy.trackingprotection.fingerprinting.enabled", True)

            # UI/Theme / prefers-color-scheme (RFP forces light to reduce fingerprint; you can override if needed)
            profile.set_preference("ui.prefers_dark_theme", False)              # Some templates set themes to standard value

            # Font enumeration reduction: (Tor/arkenfox restrict font visibility)
            # Note: Tor does more aggressive font policies, but we can at least disable font prefs that leak.
            profile.set_preference("gfx.downloadable_fonts.enabled", False)

            # Spoof timezone / locale / OS-level information (part of RFP)
            # RFP already spoofs many of these; if you want explicit control:
            profile.set_preference("privacy.resistFingerprinting.reduceTimerPrecision.microseconds", 100000)

            # Prevent WebRTC IP leak: force relay or disable
            profile.set_preference("media.peerconnection.ice.default_address_only", True)
            profile.set_preference("media.peerconnection.ice.no_host", True)

            # Misc breakage-reducing preferences (recommended by arkenfox to avoid severe breakage)
            profile.set_preference("security.enterprise_roots.enabled", False)
            profile.set_preference("dom.event.clipboardevents.enabled", False)  # prevents sites detecting copy/paste behavior
        options.profile = profile
        profile.update_preferences()
        
        driver =  webdriver.Firefox(options=options)

        for ext in extensions:

            if ext.endswith(".xpi"):

                driver.install_addon(ext)

        return driver
    

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
        choices=["chrome", "brave", "firefox"],
        help="Browser to use"
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
        _time.sleep(12)  # Increased wait time to ensure comprehensive hash is generated

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
            "Mouse Sample", "Key Press Sample", "Scroll Sample", "Touch Gestures Sample", "Comprehensive Fingerprint Hash"
        ]
        # Fill missing fields with empty string or default value
        for field in expected_fields:
            if field not in features:
                features[field] = ""

        # Map extension file names to user-friendly names
        ext_choices = []
        for ext in extensions:
            ext_lc = ext.lower()
            if "ublock" in ext_lc:
                ext_choices.append("ublock origin (lite)")
            elif "privacybadger" in ext_lc or "privacy-badger" in ext_lc or "privacy_badger" in ext_lc:
                ext_choices.append("privacy badger")
            elif "noscript" in ext_lc:
                ext_choices.append("noscript")
            elif "canvasblocker" in ext_lc:
                ext_choices.append("canvasblocker")

        # Output combined JSON
        import datetime
        timestamp = datetime.datetime.now().isoformat()
        combined_output = {
            "timestamp": timestamp,
            "config": {
            "browser": browser,
            "privacy_max": privacy_max,
            "incognito": incognito,
            "extensions": ext_choices,
            },
            "title": driver.title,
            "features": {k: features[k] for k in expected_fields}
        }
        with open("output.json", "w", encoding="utf-8") as f:
            json.dump(combined_output, f, ensure_ascii=False, indent=2)

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