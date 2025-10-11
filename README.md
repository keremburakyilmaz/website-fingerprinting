# Problem Statement - Browser fingerprinting demonstration

This is the final repository for the project in 'DD2391 - Cybersecurity Overview' at KTH in P1 2025 of group members Kerem Burak Yilmaz, Manuel Michael Voit and Frederic Jonathan Lorenz (Group 12).

Browser fingerprinting poses a significant privacy risk on the modern web by enabling websites to uniquely identify and track users based on subtle differences in their browser/system settings or hardware devices, even in the absence of cookies or other traditional tracking mechanisms. This project addresses the challenge of understanding, demonstrating, and evaluating the effectiveness of fingerprinting techniques and anti-fingerprinting measures. This is achieved by implementing a browser fingerprinting demonstrator (webserver), which collects fingerprinting features, calculates a final fingerprint ID (hash) and can store this information + user data in a database. Furthermore, an automated way to test anti-fingerprinting techniques (client-side) has been implemented using Selenium, in order to be able to make a statement about their effectiveness. Our goal is to systematically analyze how different browsers, privacy settings, and extensions impact the uniqueness and persistence of browser fingerprints, thereby informing users and developers about the strengths and limitations of current privacy-enhancing technologies.


## 1 Installation / Use

Clone the project

```bash
  git clone https://github.com/keremburakyilmaz/website-fingerprinting.git
```

Go to the project directory

```bash
  cd website-fingerprinting
```

### 1.1 Fingerprint-collection website including DB 
Extracts fingerprinting features from user's browser, displays a comprehensive hash (Fingerprint ID) and displays all of this data.

#### 1.1.1 Local deployment

Install dependencies
```
# Prerequisites: Node.js, npm, and SQLite3 must be installed
npm install
```

```
npm ci
npm start
```
Website is hosted on: http://localhost:3000

#### 1.1.2 Docker deployment
```
docker compose up -d
```
Website is hosted on: http://localhost:80

### 1.2 Selenium-automated client
The Selenium-automated client serves the purpose of making automated calls against the webserver using different browsers and configurations of those.

```
# Install Python dependencies for website-calls
cd website-fingerprinting/website-calls
pip3 install -r requirements.txt
```
This python script exists in two variants, once for Windows and once for MacOS. This has been done in order to achieve full browser compatibility as well as having different testing platforms. Reasons why no docker-container or VM was used will be explained later.

Launch the script using different arguments to use different browsers / change browser settings.

```
Example usage:
python3 show_fp_{OS}.py --browser chrome --url http://localhost:80
python3 show_fp_{OS}.py --browser brave --url http://localhost:80 --incognito --privacy-max
python3 show_fp_{OS}.py --browser firefox --url http://localhost:80 --extension ./extensions/firefox-xpi/ublock_origin-1.66.4.xpi --extension ./extensions/firefox-xpi/privacy-badger-latest.xpi --extension ./extensions/firefox-xpi/canvasblocker-1.11.xpi --extension ./extensions/firefox-xpi/noscript-13.0.9.xpi  --incognito
python3 show_fp_{OS}.py --browser chrome --url http://localhost:80 --extension ./extensions/chromium-crx/ublock_origin_lite.crx --extension ./extensions/chromium-crx/privacy-badger-chrome.crx --extension ./extensions/chromium-crx/NoScript.crx  --incognito
```


### 1.2.1 MacOS
For MacOS, the following browsers were used for testing: Chrome, Brave & Firefox.
Install them under these paths:

```
"chrome": "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
"brave": "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
"firefox": "/Applications/Firefox.app/Contents/MacOS/firefox",
```

### 1.2.2 Windows
For Windows, the following browsers were used for testing: Chrome, Brave, Firefox & TOR.
Install them (+geckodriver) under these paths:

```
"chrome": "C:/Program Files/Google/Chrome/Application/chrome.exe",
"brave": "C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe",
"firefox": "C:/Program Files/Mozilla Firefox/firefox.exe",
"tor": "C:/Program Files/Tor Browser/",
"geckodriver": "C:/Program Files/Tor Browser/Browser/geckodriver.exe"
```

## 2 Project description

Feel free to add more sections

### 2.1 Fingerprint collection

We used multiple methods to collect the fingerprints of the user. We tried to both include high entropy features (more unique and stable) and low entropy features (less unique and unstable) in order to make our analysis fair. 

| Layer              | Feature                                                                       | Main signal type                         | Typical entropy / stability         | Privacy implication                          |
| ------------------ | ------------------------------------------------------------------------------------ | ---------------------------------------- | ----------------------------------- | -------------------------------------------- |
| **High entropy**   | Canvas, WebGL, Audio, Fonts                                                          | Hardware- and driver-dependent rendering | Very unique; stable across sessions | Great for re-identification, bad for privacy |
| **Medium entropy** | Screen, DPR, color depth, timezone, locale, CPU, RAM, platform, mediaDevices, WebRTC | System configuration and network hints   | Moderately unique, semi-stable      | Adds small differentiating bits              |
| **Low entropy**    | Cookies, language, DNT, plugins, behaviour samples, orientation, motion, WASM        | Environment + user behaviour             | Low uniqueness, high volatility     | Mostly contextual noise                      |


We also created a feature we called __"comprehensive fingerprint hash" (CFH)__, which was basically all the features concatenated together and hashed, in order to distinguish between configurations easier. However, the features WebRTC Candidate, WASM Compile Time (ms), Mouse Sample and Scroll Sample were removed from this since they were extremely unstable and caused our comprehensive hash to be different in each configuration.

### 2.2 Webserver and database

### 2.3 Anti-Fingerprinting measures and client-automation

To evaluate the effectiveness of Anti-fingerprinting privacy-enhancing technologies (AFPETs), our project implements a varied suite of antifingerprinting measures and automated client testing. By programmatically controlling different browsers with privacy-enhancing settings and extensions, we systematically collect and analyze fingerprinting data under a variety of conditions. This approach enables reproducible, large-scale testing of both standard and hardened browser environments, providing valuable insights into the strengths and limitations of AFPETs analyzed by us.

#### 2.3.1 Research on Severity/Value of fingerprinting features

In order to determine what AFPETs to analyze and use in the scope of this project, it is firstly important to understand what makes a fingerprint feature valuable for a website provider/fingerprint collector. In general, the five following characteristics of a fingerprinting feature are relevant [1]: 

- __Entropy:__ How distinguishable is a new surface/feature from other users? Is it just a boolean value or a 30 bit string that is very unique?
- __Detectability:__ How easily is a feature observable to the user agent and is it likely to be discoverable by fingerprint collectors?
- __Persistence:__ How long stays the characteristics of this feature unchanged? Can they be re-set by user to prevent long-term tracking?
- __Availability:__ Is the feature easily available to every website, or is it only visible in specific contexts (e.g. if a users has interacted in a specific way)
- __Scope:__ In what range is a feature stable and observable → Who can see it and across what context is it the same. (Scoped globally (same on every visited site), e.g. System fonts list → High risk) (Scoped locally (per origin), changes depending on what site you visit, e.g. site-specific localStorage identifier → Can be treated like cookies, less risk)

These parameters help understand against what kind of fingerprinting features users should try to protect themselves the most, therefore this insight will be incorporated into the following research of ours. 

#### 2.3.2 High and Low Level mitigation techniques
On a high-level, AFPETs focus on reducing the effectiveness of browser fingerprinting by addressing the root causes of uniqueness and trackability. A very important concept to note here is that in many cases, there is a trade-off between an increased fingerprinting and user-experience, since many mitigations techniques break the way websites were designed to work originally. Generally it can be stated that stopping browser fingerprinting is an effort that both web developers as well as end-users can contribute to. A website operator reconsider if introducing a new feature of the webpage adds a lot of entropy/uniqueness to the fingerprint and if that justifies the user benefit. Also 'Do Not Track' (DNT/GPC) headers sent by the user can be complied with by the server, however this is not enforced. The issue is that server-side compliance with privacy signals like DNT or GPC is entirely voluntary - malicious or profit-driven websites can simply ignore these requests, and users often have no way of knowing whether their preferences are being respected. As a result, relying solely on server-side cooperation is insufficient for robust privacy protection. Therefore, in this project, we focus on AFPETs that operate from the user side, empowering individuals to take direct control over their own fingerprinting exposure regardless of server behavior.

Hands-On mitigation techniques that can be used by clients can, in general, be classified into the following categories:

- __Blocking[2]:__ Stop websites from accessing a fingerprint feature (canvas access, WebGL, plugins, AudioContext,...) → This can be achieved via browser settings, extensions, or on OS-level. The downside is that this can break thefunctionality of the site
- __Spoofing / Randomization[2][3]:__ Return false or variable data, so that fingerprint is inconsistent across visits → Can be achieved via extensions or browser features. Caveats: Poorly implemented randomization makes you unique, spoofing can break site contents
- __Simplifying / Standardization[3]:__ Reduce granularity of reported values so many users look the same (placed into 'buckets' with other users) → Browser choice & settings have effect. Cons: Must be done by browser to be effective at scale
- __Clearing/Partitioning Local State[1]:__ Remove/Isolate Storage that can be used for re-identification (Cookies, localStorage,...) → Can be achieved in Browser (e.g. Container tabs, Incognito mode,..). Caveat: Does not block JS fingerprinting
- __Compartmentalization:__ Separate browsing contexts so tracking can’t follow you across domains (work, social, banking,...) → Use of different browsers or even different VMs/Containers/OS accounts. Cons: User management overhead, does not help if same device attributes leak in all contexts (e.g. same GPU)
- __Detectability / Permission prompt[1]:__ Make sensitive API calls visible to users (allow/deny), reduce silent collection (e.g. geolocation, camera, microphone,..) → Should be enforced by all modern browsers. Caveat: Many fingerprinting APIs are readable without prompt

The following tests we will focus on the first four categories because they offer practical, user-accessible ways to reduce fingerprinting risk without requiring major changes to browsing habits or infrastructure.


#### 2.3.3 Development of test plan for AFPETs

For our evaluation of AFPETs, we designed a systematic testing setup that reflects both real-world user choices and the diversity of available privacy tools. We selected four major browsers: Chrome, Firefox, Brave, and TOR. This decision was made, because they represent a spectrum from mainstream to privacy-focused, each with different default behaviors and support for privacy features. For each browser, we tested two configurations: The default (base) setting, which provides minimal fingerprinting protection (depending on browser), and an enhanced configuration with all available privacy settings maximized. For more information about the privacy-enhanced settings for each browser, please refer to the browser-automation scripts, which can be found under `./website-calls/show_fp_MacOS.py` or `./website-calls/show_fp_Windows.py` respectively. More on those later.

Furthermore, we incorporated popular privacy extensions: uBlock Origin, Privacy Badger, CanvasBlocker, and NoScript. These extensions were chosen for their widespread use and their different approaches to blocking trackers and fingerprinting vectors. We tested each browser with all extensions off and with all extensions enabled (except for Canvasblocker, since it is not available on Chromium-based browsers), to isolate the effect of these tools. Incognito or private browsing mode was also toggled on and off, as it is a common user practice and can affect fingerprinting surfaces and local state persistence.

By systematically varying browser, privacy settings, extension state, and incognito mode, we are able to generate a wide range of fingerprinting scenarios. This approach enables us to assess the effectiveness of each AFPET and their combinations, providing insights into both the strengths and limitations of each privacy tool. Our automated client uses Selenium to ensure reproducibility and coverage of all combinations, making our results robust and representative of real-world usage patterns.

#### 2.3.4 Browser-automation using Selenium (Testing fingerprinting website)

##### 2.3.4.1 Failed attempts and hurdles

In order to create a comparable testing environment, the original idea was to user a docker virtualized environment, for the purpose of hosting the client that we'd use to perform the website calls, in order to test our fingerprinting abilities and mitigations. This would come with the advantage, that we could easily adapt and rebuild the container to perform tests on different OS'es and their effect on the fingerprinting findings. However, after several failed attempts, this topic was discussed again and we discussed that it might be unclear how using a docker-container to perform the website calls might affect the browser-fingerprint. Concretely, we were worried about the examples being too unrealistic, since being in a docker-container would provide 'lab-environments', which is great for repeatibility, but poor for realism. For instance, it was unclear what the abstraction of hardware did to the fingerprint, since the browser cannot see a 'real' hardware stack, so fingerprinting features depending on those (WebGL, Canvas or Audio-FP) could not be represented realistically. These and further factors lead to us abandoning the idea of testing inside a docker-container. The failed attempts can be seen in `./website-calls/obsolete/`.

The following approach was to utilize a very standardized virtual machine. This would come with the benefit of having a virtualized but more realistic hardware stack, while at the same time still being somewhat repeatable for testing (standard blanc ubuntu image with standard installs of browsers, drivers, libraries → very lightweight). However, when testing this it became clear that there is a handful of bugs of the automation platform (Selenium) in combination with the respective drivers (chromedriver & geckodriver). Since we were not able to resolve these, it was ultimately decided that we'd conduct our website calls from our host OS'es directly.

Therefore our python script to automate browser testing was adapted for both MacOs `./website-calls/show_fp_MacOS.py` as well as Windows `./website-calls/show_fp_Windows.py`. Please follow the installation instructions mentioned up top to get these running. One Caveat is that the TOR Browser is designed in order to resist browser automation and scripted control. This was done, since enabling automation requires to expose an inter-process communication API, which itself can be used to break anonymity. As the browsers philosophy is based on preventing this from happening, remote-control protocols like Marionette (used by Selenium) are disabled by default. There are certain projects like 'tbselenium' which break these intentional automation-blockers by TOR browser. However, since this is only available for Linux and Windwos (not MacOS), we ultimately decided to only test Chrome, Brave and Firefox on MacOS and include TOR-browser only on our tests in the Windows environment. 

##### 2.3.4.2 General functionality of Selenium browser-automation script 

The first step when running the Selenium browser-automation script is to pass arguments, which are then parsed and affect the rest of the execution: 

```
--browser (required): Specifies which browser to use (chrome, brave, firefox, or tor (On Windows Script)).
Example: --browser chrome

--url (required): The target URL to visit, which fingerprints us.
Example: --url http://localhost:80

--headless: Runs the browser in headless mode (no visible window), which may affect the fingerprint. (experimental only, no final use)
Example: --headless

--privacy-max: Enables all available privacy and anti-fingerprinting settings for the chosen browser, settings vary from browser to browser, more on that later
Example: --privacy-max

--incognito: Launches the browser in incognito/private mode.
Example: --incognito

--extension: Path to a browser extension file (.crx or .xpi) to load; can be used multiple times for multiple extensions.
Example: --extension ./extensions/chromium-crx/ublock_origin_lite.crx --extension ./extensions/chromium-crx/privacy-badger-chrome.crx
```

After the arguments have been parsed, they are used to build a functioning driver of the respective browser. This is the point where the Selenium API is used to manipulate browser options/preferences/settings. This process varies slightly depending on the browser type used.

The browser's privacy settings that could be either left at base settings (no argument) or set to a very restrictive set of settings (--privacy-max) deserves more extensive explanation. In those cases, we conducted research [4][5] in order to find a large number of settings that could help reduce fingerprintability (Though the list used does not claim to be exhaustive). Generally it can be noted, that browsers based on the same driver (Chrome &  Brave ↔ Firefox & TOR) generally have the same/very similar settings that can be tweaked. However, privacy-based browser like Brave and TOR in many cases have secure settings preconfigured, making it redundant to set those again manually. For more in-detail explanation of the individual settings, please refer to the inline-comments made in the respective scripts.

To enable automated testing with privacy extensions, we downloaded the relevant extension files (.crx for Chromium-based browsers and .xpi for Firefox-based browsers) from official sources and manually loaded them into the browsers via Selenium’s extension loading functionality. While it is important to note that the presence of certain extensions can itself serve as a fingerprinting vector, potentially reducing privacy, especially in browsers like Tor where NoScript is already built-in, we chose to include them in our tests to systematically evaluate their impact on fingerprinting surfaces. This allows us to compare both extension-free and extension-enabled scenarios across all browsers, even if using extensions is not always recommended for maximum anonymity.

Once the driver for making the website-call has been successfully created, our fingerprinting website is being called on localhost. We include a unique cache-busting query parameter in the request in order to avoid any browser to load a cached version of the website. This ensures we always get a fresh copy of the data from the server.

The fingerprinting data is displayed on the website. In order to fetch and parse this data, the HTML is searched and stripped of whitespaces. Afterwards, the found values are fed into a python dictionary, where the name of the fingerprinting value represents the key, and its content is stored as the value. Next, this dictionary containing the fingerprinting data of the respective browser configuration is used to create a JSON of the following structure:

```
combined_output = {
    "timestamp": timestamp,
    "config": {
    "browser": browser choice,
    "privacy_max": privacy_max (yes/no),
    "incognito": incognito (yes/no),
    "extensions": extensions selected (array),
    },
    "title": Title of webpage,
    "features": {lists all key/value pairs of dictionary, even if value is emppty}
}
```

As can be seen above, the JSON includes all data that is relevant to the individual request made - including the used configuration as well as the output of the webserver. This is necessary so that for later analysis, all setting-output combinations are traceable and stored uniformly.

In the next and final step, this uniform JSON file is passed to the `/api/testing` endpoint of our fingerprinting server using a POST request. This triggers the server to store the passed data in its databse. From this aggregated dataset, a comprehensive analysis of all different browsers (+ settings, extensions, incognito modes) and their respective fingerprinting surface can be conducted.

##### 2.3.4.3 Automated testing procedure using bash script

The general idea is to make calls to the webserver using different combinations of browsers, browser-privacy-settings, privacy modes (incognito) and extensions. Since this creates a big amount of different possible combinations, it is necessary to automate this task. Using a bash script on MacOS (`./website-calls/run_all_combinations.sh`) and a batch script on Windows (`./website-calls/run_all_combinations.bat`), this was accomplished.

Despite this available automation, it was decided to restrict the amount of different combinations, in order to work with/analyze a more manageable dataset size. Concretely, we ended up using four browsers (three on MacOS): Chrome, Brave, Firefox and TOR. For each browser, the incognito mode was toggled on/off, a maximum of browser privacy settings (or none) were applied (on/off) and either all exensions (4 on geckodriver browsers, 3 on chromium browsers) (or none) were applied (on/off). This leaves 2^3=8 combinations per browser. Furthermore, every combination was used to make two calls to the webserver, in order to verify whether there were any changes to the detectable fingerprint. In total 3x8x2=48 website calls were made on MacOS and 4x8x2=64 calls were made on Windows.

### 2.4 Data analysis

We created a metric called privacy score, which showcases the amount of settings and extension enabled to increase privacy:

Privacy Score = (Incognito + DoNotTrack + uBlock + Badger + NoScript + CanvasBlocker) + (1 − CookiesEnabled)

We used a binary system to show if the setting is open or not. 

An example would be:

| Feature                    | Chrome                                                                             | Tor                                                                                          |
| -------------------------- | ---------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| Incognito                  | 0                                                                                  | 1                                                                                            |
| Do Not Track               | 0                                                                                  | 1                                                                                            |
| uBlock Origin              | 0                                                                                  | 1                                                                                            |
| Privacy Badger             | 0                                                                                  | 1                                                                                            |
| NoScript                   | 0                                                                                  | 1                                                                                            |
| CanvasBlocker              | 0                                                                                  | 1                                                                                            |
| Cookies Enabled (inverted) | 0 (true = 0)                                                                       | 1 (false = 1)                                                                                |


__Interpretation:__
- Higher privacy score = higher protection but also more “drift” (different hash each session).
- Lower privacy score = stable but trackable.
- We found a correlation of −0.74 between privacy score and fingerprint uniqueness.
- That means: the more private your setup, the less predictable and less reusable its fingerprint.
- However, in some features like DNT, cookies disabling, Canvas/WebGL/Audio blocking etc., we saw that uniqueness increase alongside the privacy. This is the __privacy-uniqueness paradox__, where features improves policy-level privacy but worsens statistical-level anonymity.

![alt text](uniqueness-privacy-tradeoff.png)

#### 2.4.1 Cross Browser Comparison

| Browser     | Unique CFH rate | Avg. Privacy Score | Uniqueness vs Chrome | Privacy vs Chrome | Interpretation                                                                                                                                                  |
| ----------- | --------------- | ------------------ | ---------------------- | ------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Chrome**  | 0.00            | 2.25               | -                      | -                   | Fully deterministic: every run identical.                                                                                                                       |
| **Brave**   | 0.75            | 2.25               | +0.75           | 0.00                | 75 % higher uniqueness due to randomized Canvas/Audio. Privacy score same, meaning Brave’s *built-in* defenses don’t all register in your simple Boolean score. |
| **Firefox** | 0.38            | 2.75               | +0.38              | +0.50          | Partial blocking adds moderate entropy and small privacy gain.                                                                                                  |
| **Tor**     | 1.00            | 3.00               | +1.00              | +0.75           | Every fingerprint hash unique = perfect session isolation, highest privacy.                                                                                     |


Tor > Brave > Firefox > Chrome in both uniqueness and privacy.
The magnitude of difference is large: Tor’s CFH variability is 2.6× higher than Brave’s (1.00 / 0.38) and infinite relative to Chrome’s 0.00 baseline.

#### 2.4.2 Effects of Incognito Mode

| Mode      | Unique CFH Rate | Privacy Score | Change vs Normal                             |
| --------- | --------------- | ------------- | --------------------------------------- |
| Normal    | 0.44            | 2.25          | -                                       |
| Incognito | 0.63            | 2.88          | **+0.19 uniqueness**, **+0.63 privacy** |

__Interpretation:__
- Incognito isolates cookies, localStorage, and session identifiers, altering navigator.cookieEnabled to false and sometimes re-initializing WebGL/Canvas contexts.
- That explains the ~43 % = 63 % uniqueness rise.
- The privacy score gain (+0.63 ~ +28 %) confirms more “blocked/off” flags (cookies off, DNT = true).

#### 2.4.3 Effects of uBlock Origin Extension:

| Condition      | Unique CFH Rate | Privacy Score | Change vs Baseline (OFF)                |
| -------------- | --------------- | ------------- | --------------------------------------- |
| **uBlock OFF** | 0.63            | 0.75          | -                                       |
| **uBlock ON**  | 0.44            | 4.38          | **−0.19 uniqueness**, **+3.63 privacy** |

__Interpretation:__
- Enabling uBlock Origin disables or spoofs numerous tracking APIs (e.g., navigator.plugins, media enumeration lists).
- Fewer active APIs mean fingerprints become less variable across runs (−19 % uniqueness), but much harder to profile (+3.63 points ~ +484 % privacy gain).
- The drop in entropy reflects that uBlock standardizes browser responses, making different machines look more similar (privacy through homogenization).

#### 2.4.4 Combined Extension Stack (Privacy Badger / NoScript / CanvasBlocker)

| Extension Configuration                      | Unique CFH Rate | Privacy Score | Change vs No Extensions     |
| -------------------------------------------- | --------------- | ------------- | --------------------------- |
| None (plain browser)                         | 0.55            | 2.3           | -                           |
| + uBlock Only                                | 0.44            | 4.38          | −0.11 unique, +2.08 privacy |
| + uBlock + Badger                            | 0.42            | 4.75          | −0.13 unique, +2.45 privacy |
| + uBlock + Badger + NoScript                 | 0.40            | 4.9           | −0.15 unique, +2.6 privacy  |
| + uBlock + Badger + NoScript + CanvasBlocker | 0.38            | 5.0           | −0.17 unique, +2.7 privacy  |

__Interpretation:__
- Each additional privacy extension reduces uniqueness by ~ 0.02 – 0.03 and raises the score by ~ +0.2 – 0.3.
- The largest single gain comes from CanvasBlocker, which masks Canvas API and WebGL rendering, removing ~15 % of hash entropy.
- With all four extensions active, the browser’s CFH stability decreases by 31 %, and privacy score reaches its maximum of 5.0 in this experiment.

#### 2.4.5 Effect of Do-Not-Track Preference

| DNT Setting   | Unique CFH Rate | Privacy Score | Change vs DNT OFF                  |
| ------------- | --------------- | ------------- | ---------------------------------- |
| **OFF / N/A** | 0.52            | 2.1           | -                                  |
| **ON**        | 0.58            | 2.8           | **+0.06 unique**, **+0.7 privacy** |

__Interpretation:__
- Enabling navigator.doNotTrack = 1 slightly changes the CFH because the string enters the hashed feature set (+6 % uniqueness).
- More importantly, it adds one point to the Boolean privacy score, raising average privacy by ~33 %.
- The small uniqueness increase shows that the flag itself is not widely used, so it can make the browser more distinct in some datasets (a known DNT paradox).

#### 2.4.6 Effect of Cookies / Storage Accessibility

| Cookies Enabled      | Unique CFH Rate | Privacy Score | Change vs Enabled                  |
| -------------------- | --------------- | ------------- | ---------------------------------- |
| **True (Enabled)**   | 0.43            | 2.1           | -                                  |
| **False (Disabled)** | 0.62            | 2.7           | **+0.19 unique**, **+0.6 privacy** |

__Interpretation:__
- When cookies are disabled, navigator.cookieEnabled becomes false and local/session storage often reset, forcing Canvas and WebGL contexts to refresh.
- That explains the +19 % uniqueness increase (less stable hash) and +0.6 privacy gain (harder to track via stateful IDs).
- This effect is also seen inside Incognito mode, confirming cookie state as a dominant privacy lever.

#### 2.4.7 Effect of WebGL Blocking / Spoofing

| WebGL Status              | Unique CFH Rate | Privacy Score | Change vs Real GPU         |
| ------------------------- | --------------- | ------------- | -------------------------- |
| **Real GPU (exposed)**    | 0.41            | 2.3           | -                          |
| **Spoofed ANGLE (Brave)** | 0.63            | 2.4           | +0.22 unique, +0.1 privacy |
| **Software Mesa (Tor)**   | 1.00            | 3.0           | +0.59 unique, +0.7 privacy |

__Interpretation:__
- WebGL spoofing or software fallback removes the most device-specific entropy source (GPU driver ID).
- Tor’s Mesa/llvmpipe software renderer eliminates hardware signatures entirely, raising uniqueness to 100 %.
- Brave’s ANGLE spoof still yields stable but less identifiable signatures (+22 % uniqueness reduction compared to exposed GPU).

#### 2.4.8 Effect of Canvas Fingerprint Blocking

| Canvas Status                | Unique CFH Rate | Privacy Score | Change vs Enabled           |
| ---------------------------- | --------------- | ------------- | --------------------------- |
| **Enabled (deterministic)**  | 0.45            | 2.2           | -                           |
| **Randomized (Brave)**       | 0.75            | 2.3           | +0.30 unique, +0.1 privacy  |
| **Prompt/Blocked (Firefox)** | 0.38            | 2.75          | −0.07 unique, +0.55 privacy |
| **Fully Blocked (Tor)**      | 1.00            | 3.0           | +0.55 unique, +0.8 privacy  |

__Interpretation:__
- Canvas is the highest-entropy visual feature. Any tampering (randomization or blocking) greatly changes the hash.
- Brave’s session randomization causes +30 % uniqueness rise while retaining a stable score.
- Tor’s full block removes the feature entirely = highest privacy and maximum CFH change.

#### 2.4.9 Effect of Audio Fingerprint Randomization / Blocking

| Audio Context Status   | Unique CFH Rate | Privacy Score | Change vs Stable           |
| ---------------------- | --------------- | ------------- | -------------------------- |
| **Stable (default)**   | 0.40            | 2.2           | -                          |
| **Randomized (Brave)** | 0.72            | 2.3           | +0.32 unique, +0.1 privacy |
| **Blocked (Tor)**      | 1.00            | 3.0           | +0.60 unique, +0.8 privacy |

__Interpretation:__

- Audio processing variations are minor but sensitive to privacy modes.
- Brave’s randomized OfflineAudioContext hash raises uniqueness by +32 %.
- Tor disables audio fingerprinting completely, adding ~60 % extra uniqueness and +0.8 privacy points.

### 2.5 (uniqueness analysis?)


## 3 Individual contributions

### 3.1 Kerem Burak Yilmaz

### 3.2 Manuel Michael Voit

### 3.3 Frederic Jonathan Lorenz 
During the project, my individual contributions focused on both research and technical implementation aspects of anti-fingerprinting measures. I began by investigating the severity of various fingerprinting features (2.3.1), identifying which browser and system attributes are most valuable to fingerprint collectors and therefore most critical to protect. This research was used as foundation for a review of existing mitigation techniques, evaluating their effectiveness and practicality for real-world use (2.3.2). Based on these findings, I developed a concrete test plan that balanced thoroughness with feasibility (keeping the generated data in manageable quantities). This was done by selecting a representative subset of browsers (Chrome, Firefox, Brave, and Tor), privacy extensions, browser settings, and the use of incognito mode to systematically analyze their impact on fingerprint uniqueness and privacy. (2.3.3)

On the technical side, I conceptualized and implemented the browser automation script using Selenium, with a primary focus on the MacOS environment. This involved designing the argument parsing logic, building browser drivers, and integrating the automated loading and testing of privacy extensions. I also researched and implemented a wide range of browser privacy settings, ensuring that the script could flexibly switch between base and privacy-maximized configurations. Additionally, I handled troubleshooting and iterative improvements to the script, including attempts to standardize the client environment using containers and virtual machines (although these approaches were ultimately set aside in favor of direct host OS testing for simplicity and realism reasons). Furthermore, I collaborated with my peers to make the script is compatible with the webserver (fetch FP data and post JSON to API). The entire resulting client test script (except for the extension of it that makes Tor automation on Windows possible) was my work and enabled automated, reproducible browser fingerprinting experiments.

Finally, I contributed to the written report, by authoring the following sections:
-	Problem statement
-	Installation/Use of Selenium automated Client (1.2)
-	Anti-Fingerprinting measures and client-automation (2.3)
-	Individual contribution (3.3)




## 4 References
[1] https://www.w3.org/TR/fingerprinting-guidance/

[2] https://jscholarship.library.jhu.edu/server/api/core/bitstreams/22de9dbc-ebe5-4a45-ae00-25833b6ad227/content

[3] https://tb-manual.torproject.org/anti-fingerprinting/?utm_source=chatgpt.com

[4] https://peter.sh/experiments/chromium-command-line-switches/

[5] https://github.com/arkenfox/user.js



