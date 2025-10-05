const path = require('path');
const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const ajv = require("ajv").default;

const app = express();
const port = 3000;

const db = new sqlite3.Database('./db/data.db', (err) => {
    if (err) {
        console.error("Could not connect to SQLite database", err);
        process.exit(1);
    }
    console.log("Connected to SQLite database");
});

db.serialize(() => {
    db.run(`CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        behaviour INTEGER
    )`);
    db.run(`CREATE TABLE IF NOT EXISTS tests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        browser TEXT,
        privacy_max INTEGER,
        incognito INTEGER,
        ublock_origin INTEGER,
        privacy_badger INTEGER,
        noscript INTEGER,
        canvasblocker INTEGER,
        comprehensive_fingerprint_hash TEXT,
        canvas_fingerprint TEXT,
        webgl_vendor TEXT,
        webgl_renderer TEXT,
        webgl_shader_precision TEXT,
        detected_fonts TEXT,
        user_agent TEXT,
        screen_resolution TEXT,
        device_pixel_ratio TEXT,
        color_depth TEXT,
        time_zone TEXT,
        locale TEXT,
        platform TEXT,
        cpu_cores TEXT,
        device_memory_gb TEXT,
        multi_monitor_position TEXT,
        media_devices TEXT,
        webrtc_candidate TEXT,
        cookies_enabled TEXT,
        accept_language TEXT,
        do_not_track TEXT,
        plugins TEXT,
        audio_fingerprint TEXT,
        wasm_compile_time_ms TEXT,
        tls_ja3 TEXT,
        sni_dns_cert_info TEXT,
        device_motion TEXT,
        device_orientation TEXT,
        mouse_sample TEXT,
        key_press_sample TEXT,
        scroll_sample TEXT,
        touch_gestures_sample TEXT
    )`);
});

const schema_testing_api = require("./testing_api_schema.json");
const ajv_validator = new ajv();
const validate_testing_api = ajv_validator.compile(schema_testing_api);

app.set('view engine', 'ejs');
app.use(express.static(path.join(__dirname, 'public')));
app.use(express.json());


app.get('/', (req, res) => {
    res.render('index');
});

app.get('/api/fingerprint', async (req, res) => {
    const fingerprintId = req.query.fingerprintId;
    if (!fingerprintId) {
        return res.status(400).json({ success: false, message: 'FingerprintId is required.' });
    }

    try {
        const storedBehaviour = await new Promise((resolve, reject) => {
            db.get("SELECT behaviour FROM users WHERE id = ?", [fingerprintId], (err, row) => {
                if (err) reject(err);
                else resolve(row);
            });
        });

        if (!storedBehaviour) {
            return res.status(404).json({ success: false, message: 'No stored behaviour for fingerprintId.' });
        }
        
        res.json({
            fingerprintId: fingerprintId,
            behaviour: storedBehaviour.behaviour,
        });
    } catch (error) {
        console.error('Error retrieving behaviour: ', error);
        res.status(500).json({ error: 'Failed to retrieve behaviour' });
    }
});

app.post('/api/fingerprint', async (req, res) => {
    const { fingerprintId, behaviour } = req.body;
    if (!fingerprintId || !behaviour) {
        return res.status(400).json({ success: false, message: 'FingerprintId and behaviour are required.' });
    }

    try {
        await new Promise((resolve, reject) => {
            db.run("INSERT INTO users (id, behaviour) VALUES (?, ?) ON CONFLICT(id) DO UPDATE SET behaviour = (?)",
                [fingerprintId, behaviour, behaviour], (err) => {
                    if (err) reject(err);
                    else resolve();
                });
        });

        res.json({ success: true, message: 'FingerprintId and behaviour saved correctly!' });
    } catch (error) {
        console.error('Error adding fingerprintId: ', error);
        res.status(500).json({ error: 'Failed to add fingerprintId' });
    }
});

app.post('/api/testing', async (req, res) => {
    if (!validate_testing_api(req.body)) {
        return res.status(400).json({ success: false, message: 'Body does not match the required JSON schema for the endpoint.' });
    }
    
    const { 
        timestamp, 
        config: {
            browser, 
            privacy_max, 
            incognito, 
            extensions 
        }, 
        features: {
            "Comprehensive Fingerprint Hash": comprehensive_fingerprint_hash,
            "Canvas Fingerprint": canvas_fingerprint,
             "WebGL Vendor": webgl_vendor,
            "WebGL Renderer": webgl_renderer,
            "WebGL Shader Precision": webgl_shader_precision,
            "Detected Fonts": detected_fonts,
            "User-Agent": user_agent,
            "Screen Resolution": screen_resolution,
            "Device Pixel Ratio": device_pixel_ratio,
            "Color Depth": color_depth,
            "Time Zone": time_zone,
            "Locale": locale,
            "Platform": platform,
            "CPU Cores": cpu_cores,
            "Device Memory (GB)": device_memory_gb,
            "Multi-Monitor Position": multi_monitor_position,
            "Media Devices": media_devices,
            "WebRTC Candidate": webrtc_candidate,
            "Cookies Enabled": cookies_enabled,
            "Accept-Language":accept_language,
            "Do Not Track": do_not_track,
            "Plugins": plugins,
            "Audio Fingerprint": audio_fingerprint,
            "WASM Compile Time (ms)": wasm_compile_time_ms,
            "TLS / JA3": tls_ja3,
            "SNI / DNS / Cert Info": sni_dns_cert_info,
            "Device Motion": device_motion,
            "Device Orientation": device_orientation,
            "Mouse Sample": mouse_sample,
            "Key Press Sample": key_press_sample,
            "Scroll Sample": scroll_sample,
            "Touch Gestures Sample": touch_gestures_sample
        } 
    } = req.body;
    
    ublock_origin = extensions.findIndex(elm => elm.includes("ublock origin (lite)")) === -1 ? 0 : 1;
    privacy_badger = extensions.findIndex(elm => elm.includes("privacy badger")) === -1 ? 0 : 1;
    noscript = extensions.findIndex(elm => elm.includes("noscript")) === -1 ? 0 : 1;
    canvasblocker = extensions.findIndex(elm => elm.includes("canvasblocker")) === -1 ? 0 : 1;

    try {
        await new Promise((resolve, reject) => {
            db.run(`INSERT INTO tests (
                        timestamp,
                        browser,
                        privacy_max,
                        incognito,
                        ublock_origin,
                        privacy_badger,
                        noscript,
                        canvasblocker,
                        comprehensive_fingerprint_hash,
                        canvas_fingerprint,
                        webgl_vendor,
                        webgl_renderer,
                        webgl_shader_precision,
                        detected_fonts,
                        user_agent,
                        screen_resolution,
                        device_pixel_ratio,
                        color_depth,
                        time_zone,
                        locale,
                        platform,
                        cpu_cores,
                        device_memory_gb,
                        multi_monitor_position,
                        media_devices,
                        webrtc_candidate,
                        cookies_enabled,
                        accept_language,
                        do_not_track,
                        plugins,
                        audio_fingerprint,
                        wasm_compile_time_ms,
                        tls_ja3,
                        sni_dns_cert_info,
                        device_motion,
                        device_orientation,
                        mouse_sample,
                        key_press_sample,
                        scroll_sample,
                        touch_gestures_sample
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
                [
                    timestamp,
                    browser,
                    privacy_max,
                    incognito,
                    ublock_origin,
                    privacy_badger,
                    noscript,
                    canvasblocker,
                    comprehensive_fingerprint_hash,
                    canvas_fingerprint,
                    webgl_vendor,
                    webgl_renderer,
                    webgl_shader_precision,
                    detected_fonts,
                    user_agent,
                    screen_resolution,
                    device_pixel_ratio,
                    color_depth,
                    time_zone,
                    locale,
                    platform,
                    cpu_cores,
                    device_memory_gb,
                    multi_monitor_position,
                    media_devices,
                    webrtc_candidate,
                    cookies_enabled,
                    accept_language,
                    do_not_track,
                    plugins,
                    audio_fingerprint,
                    wasm_compile_time_ms,
                    tls_ja3,
                    sni_dns_cert_info,
                    device_motion,
                    device_orientation,
                    mouse_sample,
                    key_press_sample,
                    scroll_sample,
                    touch_gestures_sample
                ], (err) => {
                    if (err) reject(err);
                    else resolve();
                });
        });

        res.json({ success: true, message: 'Test results saved correctly!' });
    } catch (error) {
        console.error('Error adding test results: ', error);
        res.status(500).json({ error: 'Failed to add fingerprint and config' });
    }
});

const server = app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
});

// Handle shutdown gracefully
process.on("SIGTERM", () => {
  console.log("SIGTERM received, shutting down...");
  server.close(() => {
    console.log("HTTP server closed");
    process.exit(0);
  });
});

process.on("SIGINT", () => {
  console.log("SIGINT received, shutting down...");
  server.close(() => {
    console.log("HTTP server closed");
    process.exit(0);
  });
});
