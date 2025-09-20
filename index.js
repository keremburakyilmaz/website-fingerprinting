const path = require('path');
const express = require('express');
const sqlite3 = require('sqlite3').verbose();

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
});

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
