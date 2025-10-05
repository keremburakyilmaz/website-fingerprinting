## Deterministic browser automation image: pin specific versions of Chrome + chromedriver, Brave, Firefox ESR, geckodriver, Tor.
## Build for linux/amd64 (set platform in docker-compose for Apple Silicon hosts).

FROM ubuntu:22.04

## Chrome/Chromedriver version 140.0.7339.207 (from chrome-for-testing)
ARG BRAVE_VERSION=1.60.118
ARG FIREFOX_VERSION=115.9.1esr
ARG GECKODRIVER_VERSION=v0.34.0

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    PYTHONUNBUFFERED=1

WORKDIR /client

# Base system deps & shared libraries needed by browsers
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl wget gnupg2 unzip tar xz-utils jq procps file \
    fonts-liberation libasound2 libatk-bridge2.0-0 libnss3 libxkbcommon0 libxdamage1 libxcomposite1 libxrandr2 libxfixes3 libxext6 libx11-6 libgbm1 libgtk-3-0 libdrm2 libxshmfence1 libxss1 libu2f-udev libxtst6 libpci3 \
    tor python3 python3-pip \
    && rm -rf /var/lib/apt/lists/*


# --- Chrome (from chrome-for-testing, version 140.0.7339.207) ---
RUN set -eux; \
    cd /tmp; \
    wget -q https://storage.googleapis.com/chrome-for-testing-public/117.0.5938.92/linux64/chrome-linux64.zip; \
    unzip chrome-linux64.zip; \
    mv chrome-linux64/chrome /usr/local/bin/google-chrome; \
    chmod +x /usr/local/bin/google-chrome; \
    rm -rf chrome-linux64* chrome-linux64.zip


# --- Chromedriver (from chrome-for-testing, version 140.0.7339.207) ---
RUN set -eux; \
    cd /tmp; \
    wget -q https://storage.googleapis.com/chrome-for-testing-public/117.0.5938.92/linux64/chromedriver-linux64.zip; \
    unzip chromedriver-linux64.zip; \
    mv chromedriver-linux64/chromedriver /usr/local/bin/chromedriver; \
    chmod +x /usr/local/bin/chromedriver; \
    rm -rf chromedriver-linux64* chromedriver-linux64.zip



# Create an unprivileged user to run browsers (recommended for Chrome/Firefox sandbox)
# RUN useradd -m -u 1000 runner && mkdir -p /home/runner/downloads && chown -R runner:runner /home/runner
# ENV HOME=/home/runner
# USER runner
ENV HOME=/root
USER root


# Python deps
COPY requirements.txt ./requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY show_fp.py ./show_fp.py

ENV CHROME_BIN=/usr/local/bin/google-chrome \
    BRAVE_BIN=/usr/bin/brave-browser \
    FIREFOX_BIN=/usr/local/bin/firefox \
    CHROMEDRIVER_PATH=/usr/local/bin/chromedriver \
    GECKODRIVER_PATH=/usr/local/bin/geckodriver

CMD ["python", "show_fp.py", "--help"]