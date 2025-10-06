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

## 2 Project description

FEEL FREE TO ADD MORE SECTIONS

### 2.1 Fingerprint collection

### 2.2 Webserver and database

### 2.3 Anti-Fingerprinting measures and client-automation

### 2.4 Data analysis

### 2.5 (uniqueness analysis?)


## 3 Individual contributions

### 3.1 Kerem Burak Yilmaz

### 3.2 Manuel Michael Voit

### 3.3 Frederic Jonathan Lorenz 

