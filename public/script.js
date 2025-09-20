async function create_fingerprint() {
    // Utility: append a feature card to the list
    function addFeature(title, value) {
        const ul = document.getElementById('featureList');
        const li = document.createElement('li');
        li.id = title.replace(/ /g, "");
        li.className = 'card';
        const safeVal = (typeof value === 'string' || typeof value === 'number')
        ? String(value)
        : JSON.stringify(value, null, 2);
        li.innerHTML = '<h3>' + escapeHtml(title) + '</h3><pre>' + escapeHtml(safeVal) + '</pre>';
        ul.appendChild(li);
    }

    function escapeHtml(s) {
        return String(s)
        .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
        .replace(/"/g,'&quot;').replace(/'/g,'&#039;');
    }

    // SHA-256 helper (returns hex)
    // used to turn high-entropy raw data (like canvas pixel bytes or audio samples) into a stable short identifier that can be displayed or compared
    async function sha256Hex(input) {
        const data = (typeof input === 'string') ? new TextEncoder().encode(input) : input;
        const hash = await crypto.subtle.digest('SHA-256', data);
        return Array.from(new Uint8Array(hash)).map(b => b.toString(16).padStart(2,'0')).join('');
    }

    // ========= HIGH ENTROPY FEATURES =========
    // These are the strongest identifiers – usually enough to uniquely identify a device.

    // 1. Canvas fingerprint: draw text/images and hash rendering differences
    await (async function canvasFP() {
        try {
        const canvas = document.createElement("canvas");
        const ctx = canvas.getContext("2d");
        ctx.font = "16px Arial";
        ctx.fillText("Canvas FP Test 😃 測試", 10, 20);
        const hash = await sha256Hex(ctx.getImageData(0, 0, 200, 50).data.buffer);
        addFeature("Canvas Fingerprint", hash);
        } catch {
        addFeature("Canvas Fingerprint", "Blocked");
        }
    })();

    // 2. WebGL fingerprint: GPU vendor, renderer, shader precision
    (function webglFP() {
        try {
        const gl = document.createElement("canvas").getContext("webgl");
        if (!gl) return addFeature("WebGL", "Not supported");
        const ext = gl.getExtension("WEBGL_debug_renderer_info");
        const vendor = ext ? gl.getParameter(ext.UNMASKED_VENDOR_WEBGL) : "N/A";
        const renderer = ext ? gl.getParameter(ext.UNMASKED_RENDERER_WEBGL) : "N/A";
        addFeature("WebGL Vendor", vendor);
        addFeature("WebGL Renderer", renderer);
        addFeature("WebGL Shader Precision", gl.getShaderPrecisionFormat(gl.VERTEX_SHADER, gl.HIGH_FLOAT));
        } catch {
        addFeature("WebGL", "Blocked");
        }
    })();

    // 3. Audio fingerprint: subtle differences in sound processing
    (async function audioFP() {
        try {
        const OfflineCtx = window.OfflineAudioContext || window.webkitOfflineAudioContext;
        if (!OfflineCtx) return addFeature("Audio Fingerprint", "Not supported");
        const ctx = new OfflineCtx(1, 44100, 44100);
        const osc = ctx.createOscillator();
        osc.connect(ctx.destination);
        osc.start();
        ctx.startRendering();
        const rendered = await new Promise(res => ctx.oncomplete = e => res(e.renderedBuffer));
        const hash = await sha256Hex(rendered.getChannelData(0).buffer);
        addFeature("Audio Fingerprint", hash);
        } catch {
        addFeature("Audio Fingerprint", "Blocked");
        }
    })();

    // 4. Fonts: detect installed fonts by measuring text rendering widths
    (function fontProbe() {
        const baseFonts = ["monospace","serif","sans-serif"];
        const fontsToTest = ["Arial","Times New Roman","Courier New","Roboto","Comic Sans MS"];
        function measure(font) {
        const span = document.createElement("span");
        span.style.font = "16px " + font;
        span.textContent = "mmmmmmmmmlliI";
        document.body.appendChild(span);
        const w = span.getBoundingClientRect().width;
        document.body.removeChild(span);
        return w;
        }
        const baseline = {}; baseFonts.forEach(f => baseline[f] = measure(f));
        const detected = [];
        fontsToTest.forEach(f => {
        const w = measure(f + "," + baseFonts.join(","));
        if (!baseFonts.some(b => Math.abs(w - baseline[b]) < 0.1)) detected.push(f);
        });
        addFeature("Detected Fonts", detected);
    })();

    // 5. User-Agent: browser + OS info
    addFeature("User-Agent", navigator.userAgent);

    // ========= MEDIUM ENTROPY FEATURES =========
    // Adds uniqueness but weaker than above

    // Screen / display properties
    addFeature("Screen Resolution", screen.width + " x " + screen.height);
    addFeature("Device Pixel Ratio", window.devicePixelRatio);
    addFeature("Color Depth", screen.colorDepth);

    // Time zone & locale
    addFeature("Time Zone", Intl.DateTimeFormat().resolvedOptions().timeZone);
    addFeature("Locale", Intl.NumberFormat().resolvedOptions().locale);

    // Platform, CPU, RAM
    addFeature("Platform", navigator.platform);
    addFeature("CPU Cores", navigator.hardwareConcurrency || "N/A");
    addFeature("Device Memory (GB)", navigator.deviceMemory || "N/A");

    // Multi-monitor info
    addFeature("Multi-Monitor Position", `availLeft=${screen.availLeft || 0}, availTop=${screen.availTop || 0}`);

    // Media devices (mics, cams, speakers)
    (async function mediaDevices() {
        try {
        const devices = await navigator.mediaDevices.enumerateDevices();
        addFeature("Media Devices", devices.map(d => `${d.kind}: ${d.label || "hidden"}`));
        } catch {
        addFeature("Media Devices", "Blocked or denied");
        }
    })();

    // WebRTC IP discovery (may expose local/public IPs if not blocked)
    (function webrtcIPs() {
        try {
        const pc = new RTCPeerConnection();
        pc.createDataChannel("");
        pc.onicecandidate = e => {
            if (e.candidate) addFeature("WebRTC Candidate", e.candidate.candidate);
        };
        pc.createOffer().then(o => pc.setLocalDescription(o));
        setTimeout(() => pc.close(), 1500);
        } catch {
        addFeature("WebRTC", "Blocked");
        }
    })();

    // ========= LOWER ENTROPY / CONTEXTUAL =========
    // Adds small bits of uniqueness or context, but not strong identifiers

    addFeature("Cookies Enabled", navigator.cookieEnabled);
    addFeature("Accept-Language", navigator.language);
    addFeature("Do Not Track", navigator.doNotTrack || "N/A");

    try {
        const plugins = Array.from(navigator.plugins || []).map(p => p.name);
        addFeature("Plugins", plugins.length ? plugins : "None");
    } catch {
        addFeature("Plugins", "Blocked");
    }

    // Behavioral samples: mouse, key, scroll
    (function behavior() {
        const mouse = [], keys = [], scrolls = [];
        window.addEventListener("mousemove", e => { if (mouse.length<3) mouse.push([e.clientX,e.clientY]); });
        window.addEventListener("keydown", e => { if (keys.length<3) keys.push(e.key); });
        window.addEventListener("scroll", e => { if (scrolls.length<3) scrolls.push([scrollX,scrollY]); });
        setTimeout(() => {
        addFeature("Mouse Sample", mouse);
        addFeature("Key Press Sample", keys);
        addFeature("Scroll Sample", scrolls);
        }, 4000);
    })();

    // Orientation & motion sensors (mobile devices)
    window.addEventListener("deviceorientation", e => {
        addFeature("Device Orientation", {alpha:e.alpha,beta:e.beta,gamma:e.gamma});
    }, {once:true});

    window.addEventListener("devicemotion", e => {
        addFeature("Device Motion", {
        acc: e.acceleration,
        accG: e.accelerationIncludingGravity,
        rot: e.rotationRate
        });
    }, {once:true});

    // Touch gestures (sample logs)
    const touches = [];
    window.addEventListener("touchstart", e => touches.push("start " + e.touches.length));
    window.addEventListener("touchend", e => touches.push("end"));
    setTimeout(() => addFeature("Touch Gestures Sample", touches), 5000);

    // WASM performance micro-benchmark
    (async function wasmPerf() {
        try {
        const start = performance.now();
        const mod = await WebAssembly.compile(new Uint8Array([0,97,115,109,1,0,0,0]));
        await WebAssembly.instantiate(mod);
        addFeature("WASM Compile Time (ms)", (performance.now()-start).toFixed(2));
        } catch {
        addFeature("WASM Perf", "Not supported");
        }
    })();

    // TLS / DNS / Cert info – only available to network observers
    addFeature("TLS / JA3", "Unavailable in browser JS");
    addFeature("SNI / DNS / Cert Info", "Unavailable in browser JS");
}

async function fingerprint() {
    await create_fingerprint();
    const btnBehaviour = document.getElementById('btnBehaviour');
    const btnSubmit = document.getElementById('btnSubmit');
    const canvas_fingerprint = document.getElementById('CanvasFingerprint').getElementsByTagName('pre')[0].textContent;

    async function load_behaviour() {
        try {
            const response = await fetch('/api/fingerprint?fingerprintId=' + canvas_fingerprint);
            if (!response.ok) {
                throw new Error(`Response status: ${response.status}`);
            }
            const data = await response.json();
            btnBehaviour.innerText = data.behaviour;
        } catch (error) {
        }
    }

    load_behaviour();

    btnBehaviour.addEventListener('click', () => {
        btnBehaviour.innerText = Number(btnBehaviour.innerText) + 1;
    });

    btnSubmit.addEventListener('click', async () => {
        const behaviour = btnBehaviour.innerText;
        try {
            const response = await fetch('/api/fingerprint', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ fingerprintId: canvas_fingerprint, behaviour: behaviour })
            });
        } catch (error) {
            console.error("Error:", error);
        }   
    });
}

fingerprint();