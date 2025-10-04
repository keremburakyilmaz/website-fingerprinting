#!/bin/bash
# Automated test runner for show_fp_local.py with all browser/privacy/extension/incognito combinations

SCRIPT="show_fp_local.py"
URL="http://localhost:80"
EXT_CHROME="./extensions/chromium-crx/ublock_origin_lite.crx ./extensions/chromium-crx/privacy_badger-chrome.crx ./extensions/chromium-crx/NoScript.crx"
EXT_FIREFOX="./extensions/firefox-xpi/ublock_origin-1.66.4.xpi ./extensions/firefox-xpi/privacy-badger-latest.xpi ./extensions/firefox-xpi/canvasblocker-1.11.xpi ./extensions/firefox-xpi/noscript-13.0.9.xpi"
BROWSERS=(chrome brave firefox)
PRIVACY=("" "--privacy-max")
EXTENSIONS=("" "--extension-all")
INCOGNITO=("" "--incognito")

for BROWSER in "${BROWSERS[@]}"; do
  for PRIV in "${PRIVACY[@]}"; do
    for EXT in "" "all"; do
      for INCOG in "" "--incognito"; do
        CMD="python3 $SCRIPT --browser $BROWSER --url $URL $PRIV $INCOG"
        # Only add extensions if EXT==all and the files exist for the browser
        if [ "$EXT" = "all" ]; then
          if [ "$BROWSER" = "firefox" ]; then
            for XPI in $EXT_FIREFOX; do
              if [ -f "$XPI" ]; then
                CMD+=" --extension $XPI"
              fi
            done
          else
            for CRX in $EXT_CHROME; do
              if [ -f "$CRX" ]; then
                CMD+=" --extension $CRX"
              fi
            done
          fi
        fi
        echo "Running: $CMD"
        eval $CMD
        echo "Sleeping 10 seconds..."
        sleep 10
      done
    done
  done
done
