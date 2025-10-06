@echo off
REM Automated test runner for show_fp_Windows.py with all browser/privacy/extension/incognito combinations

set SCRIPT=show_fp_Windows.py
set URL=http://localhost:3000

set SCRIPT_PATH=%~dp0
set PYTHON_PATH="%SCRIPT_PATH%.venv\Scripts\python.exe"

set EXT_CHROME=extensions\chromium-crx\ublock_origin_lite.crx extensions\chromium-crx\privacy-badger-chrome.crx extensions\chromium-crx\NoScript.crx
set EXT_FIREFOX=extensions\firefox-xpi\ublock_origin-1.66.4.xpi extensions\firefox-xpi\privacy-badger-latest.xpi extensions\firefox-xpi\canvasblocker-1.11.xpi extensions\firefox-xpi\noscript-13.0.9.xpi

REM Define browsers, privacy, extensions, and incognito settings
set BROWSERS=chrome brave firefox tor
set PRIVACY=_none_ --privacy-max
set EXTENSIONS=_none_ all
set INCOGNITO=_none_ --incognito

setlocal enabledelayedexpansion

REM Loop through all possible combinations 
REM Browser choice: Chrome, Brave, Firefox, Tor; Incognito: True, False; Max privacy settings: True, False; Extensions: None, All
REM Perform this loop twice to see variability (has fingerprint changed for the same config?)
for /l %%R in (1,1,2) do (
    for %%B in (%BROWSERS%) do (
        for %%P in (%PRIVACY%) do (
            for %%E in (%EXTENSIONS%) do (
                for %%I in (%INCOGNITO%) do (
                    set CMD=%PYTHON_PATH% %SCRIPT% --browser %%B --url %URL%

                    if not "%%P"=="_none_" (
                        set CMD=!CMD! %%P
                    )

                    if not "%%I"=="_none_" (
                        set CMD=!CMD! %%I
                    )

                    REM Add extensions if requested
                    if "%%E"=="all" (
                        if "%%B"=="firefox" (
                            for %%X in (%EXT_FIREFOX%) do (
                                if exist "%SCRIPT_PATH%%%X" (
                                    set CMD=!CMD! --extension "%SCRIPT_PATH%%%X"
                                )
                            )
                        ) else if "%%B"=="tor" (
                            for %%X in (%EXT_FIREFOX%) do (
                                if exist "%SCRIPT_PATH%%%X" (
                                    set CMD=!CMD! --extension "%SCRIPT_PATH%%%X"
                                )
                            )
                        ) else (
                            for %%X in (%EXT_CHROME%) do (
                                if exist "%SCRIPT_PATH%%%X" (
                                    set CMD=!CMD! --extension "%SCRIPT_PATH%%%X"
                                )
                            )
                        )
                    )

                    echo Running ^(repeat %%R^): !CMD!
                    cmd /c "!CMD!"
                    echo --------------------------------------------------------------
                    echo:
                )
            )
        )
    )
)

endlocal
