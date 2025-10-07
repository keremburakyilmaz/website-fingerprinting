# Browser fingerprinting demonstration
This is the final repository for the project in 'DD2391 - Cybersecurity Overview' at KTH in P1 2025 of group members Kerem Burak Yilmaz, Manuel Michael Voit and Frederic Jonathan Lorenz (Group 12). This project implements a browser fingerprinting demonstrator (webserver), which collects fingerprinting features, calculates a final fingerprint ID and can store this information + user behaviour in a DB. Furthermore, an automated way to test anti-fingerprinting techniques (client-side) has been implemented using Selenium, in order to be able to make a statement about their effectiveness.


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

## 2 Problem Statement

Needs to be added (required according to canvas page)

## 3 Project description

Feel free to add more sections

### 3.1 Fingerprint collection

### 3.2 Webserver and database

### 3.3 Anti-Fingerprinting measures and client-automation

To evaluate the effectiveness of Anti-fingerprinting privacy-enhancing technologies (AFPETs), our project implements a varied suite of antifingerprinting measures and automated client testing. By programmatically controlling different browsers with privacy-enhancing settings and extensions, we systematically collect and analyze fingerprinting data under a variety of conditions. This approach enables reproducible, large-scale testing of both standard and hardened browser environments, providing valuable insights into the strengths and limitations of AFPETs analyzed by us.

#### 3.3.1 Research on Severity/Value of fingerprinting features

In order to determine what AFPETs to analyze and use in the scope of this project, it is firstly important to understand what makes a fingerprint feature valuable for a website provider/fingerprint collector. In general, the five following characteristics of a fingerprinting feature are relevant [1]: 

- __Entropy:__ How distinguishable is a new surface/feature from other users? Is it just a boolean value or a 30 bit string that is very unique?
- __Detectability:__ How easily is a feature observable to the user agent and is it likely to be discoverable by fingerprint collectors?
- __Persistence:__ How long stays the characteristics of this feature unchanged? Can they be re-set by user to prevent long-term tracking?
- __Availability:__ Is the feature easily available to every website, or is it only visible in specific contexts (e.g. if a users has interacted in a specific way)
- __Scope:__ In what range is a feature stable and observable → Who can see it and across what context is it the same. (Scoped globally (same on every visited site), e.g. System fonts list → High risk) (Scoped locally (per origin), changes depending on what site you visit, e.g. site-specific localStorage identifier → Can be treated like cookies, less risk)

These parameters help understand against what kind of fingerprinting features users should try to protect themselves the most, therefore this insight will be incorporated into the following research of ours. 

#### 3.3.2 High and Low Level mitigation techniques
On a high-level, AFPETs focus on reducing the effectiveness of browser fingerprinting by addressing the root causes of uniqueness and trackability. A very important concept to note here is that in many cases, there is a trade-off between an increased fingerprinting and user-experience, since many mitigations techniques break the way websites were designed to work originally. Generally it can be stated that stopping browser fingerprinting is an effort that both web developers as well as end-users can contribute to. A website operator reconsider if introducing a new feature of the webpage adds a lot of entropy/uniqueness to the fingerprint and if that justifies the user benefit. Also 'Do Not Track' (DNT/GPC) headers sent by the user can be complied with by the server, however this is not enforced. The issue is that server-side compliance with privacy signals like DNT or GPC is entirely voluntary — malicious or profit-driven websites can simply ignore these requests, and users often have no way of knowing whether their preferences are being respected. As a result, relying solely on server-side cooperation is insufficient for robust privacy protection. Therefore, in this project, we focus on AFPETs that operate from the user side, empowering individuals to take direct control over their own fingerprinting exposure regardless of server behavior.

Hands-On mitigation techniques that can be used by clients can, in general, be classified into the following categories:

- __Blocking[2]:__ Stop websites from accessing a fingerprint feature (canvas access, WebGL, plugins, AudioContext,...) → This can be achieved via browser settings, extensions, or on OS-level. The downside is that this can break thefunctionality of the site
- __Spoofing / Randomization[2][3]:__ Return false or variable data, so that fingerprint is inconsistent across visits → Can be achieved via extensions or browser features. Caveats: Poorly implemented randomization makes you unique, spoofing can break site contents
- __Simplifying / Standardization[3]:__ Reduce granularity of reported values so many users look the same (placed into 'buckets' with other users) → Browser choice & settings have effect. Cons: Must be done by browser to be effective at scale
- __Clearing/Partitioning Local State[1]:__ Remove/Isolate Storage that can be used for re-identification (Cookies, localStorage,...) → Can be achieved in Browser (e.g. Container tabs, Incognito mode,..). Caveat: Does not block JS fingerprinting
- __Compartmentalization:__ Separate browsing contexts so tracking can’t follow you across domains (work, social, banking,...) → Use of different browsers or even different VMs/Containers/OS accounts. Cons: User management overhead, does not help if same device attributes leak in all contexts (e.g. same GPU)
- __Detectability / Permission prompt[1]:__ Make sensitive API calls visible to users (allow/deny), reduce silent collection (e.g. geolocation, camera, microphone,..) → Should be enforced by all modern browsers. Caveat: Many fingerprinting APIs are readable without prompt

The following tests we will focus on the first four categories because they offer practical, user-accessible ways to reduce fingerprinting risk without requiring major changes to browsing habits or infrastructure.


#### 3.3.3 Development of test plan for AFPETs

For our evaluation of AFPETs, we designed a systematic testing setup that reflects both real-world user choices and the diversity of available privacy tools. We selected four major browsers: Chrome, Firefox, Brave, and TOR. This decision was made, because they represent a spectrum from mainstream to privacy-focused, each with different default behaviors and support for privacy features. For each browser, we tested two configurations: The default (base) setting, which provides minimal fingerprinting protection (depending on browser), and an enhanced configuration with all available privacy settings maximized. For more information about the privacy-enhanced settings for each browser, please refer to the browser-automation scripts, which can be found under `./website-calls/show_fp_MacOS.py` or `./website-calls/show_fp_Windows.py` respectively. More on those later.

Furthermore, we incorporated popular privacy extensions: uBlock Origin, Privacy Badger, CanvasBlocker, and NoScript. These extensions were chosen for their widespread use and their different approaches to blocking trackers and fingerprinting vectors. We tested each browser with all extensions off and with all extensions enabled (except for Canvasblocker, since it is not available on Chromium-based browsers), to isolate the effect of these tools. Incognito or private browsing mode was also toggled on and off, as it is a common user practice and can affect fingerprinting surfaces and local state persistence.

By systematically varying browser, privacy settings, extension state, and incognito mode, we are able to generate a wide range of fingerprinting scenarios. This approach enables us to assess the effectiveness of each AFPET and their combinations, providing insights into both the strengths and limitations of each privacy tool. Our automated client uses Selenium to ensure reproducibility and coverage of all combinations, making our results robust and representative of real-world usage patterns.

#### 3.3.4 Browser-automation using Selenium (Testing fingerprinting website)

##### 3.3.4.1 Failed attempts

##### 3.3.4.2 General functionality of script

##### 3.3.4.3 Automated testing procedure using bash script

### 3.4 Data analysis

### 3.5 (uniqueness analysis?)


## 4 Individual contributions

### 4.1 Kerem Burak Yilmaz

### 4.2 Manuel Michael Voit

### 4.3 Frederic Jonathan Lorenz 

## 5 References
[1] https://www.w3.org/TR/fingerprinting-guidance/

[2] https://jscholarship.library.jhu.edu/server/api/core/bitstreams/22de9dbc-ebe5-4a45-ae00-25833b6ad227/content

[3] https://tb-manual.torproject.org/anti-fingerprinting/?utm_source=chatgpt.com

