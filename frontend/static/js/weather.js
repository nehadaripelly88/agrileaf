/**
 * AgriLeaf — weather.js
 * Weather-based disease risk alerts using Open-Meteo (free, no API key needed)
 */

const DISEASE_RISK_RULES = [
    {
        condition: d => d.humidity > 85 && d.temp > 20 && d.temp < 30,
        risk: 'HIGH',
        message: '⚠️ High humidity + warm temp: HIGH RISK of Late Blight (Tomato/Potato) and Leaf Blast (Rice). Spray preventive fungicide today.',
        level: 'danger'
    },
    {
        condition: d => d.humidity > 80 && d.rain > 0,
        risk: 'HIGH',
        message: '🌧️ Wet conditions detected: HIGH RISK of Bacterial diseases and fungal infections. Avoid field work. Apply Copper Oxychloride.',
        level: 'danger'
    },
    {
        condition: d => d.temp > 15 && d.temp < 25 && d.humidity > 70,
        risk: 'MEDIUM',
        message: '⚠️ Cool moist weather: MEDIUM RISK of Wheat Rust and Rice Blast. Monitor fields closely.',
        level: 'warning'
    },
    {
        condition: d => d.temp > 35 && d.humidity < 40,
        risk: 'MEDIUM',
        message: '🔥 Hot dry conditions: MEDIUM RISK of Spider Mites and Powdery Mildew. Increase irrigation.',
        level: 'warning'
    },
    {
        condition: d => d.humidity > 60 && d.humidity <= 80 && d.rain === 0,
        risk: 'LOW',
        message: '✅ Weather conditions are currently favourable. Low disease risk. Continue regular monitoring.',
        level: 'good'
    }
];

async function fetchWeatherAndShowAlert() {
    const bar = document.getElementById('weatherAlertBar');
    if (!bar) return;

    try {
        // Get user location
        if (!navigator.geolocation) { showFallbackAlert(bar); return; }

        navigator.geolocation.getCurrentPosition(async pos => {
            try {
                const { latitude, longitude } = pos.coords;
                // Open-Meteo — completely free, no API key
                const url = `https://api.open-meteo.com/v1/forecast?latitude=${latitude}&longitude=${longitude}&current=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m&timezone=auto`;
                const res = await fetch(url);
                const data = await res.json();
                const cur = data.current;

                const weatherData = {
                    temp: cur.temperature_2m,
                    humidity: cur.relative_humidity_2m,
                    rain: cur.precipitation,
                    wind: cur.wind_speed_10m
                };

                const matched = DISEASE_RISK_RULES.find(r => r.condition(weatherData));
                if (matched) {
                    const colors = {
                        danger:  {bg:'#fef2f2', border:'#fca5a5', text:'#991b1b', badge:'#dc2626', badgetxt:'#fff'},
                        warning: {bg:'#fffbeb', border:'#fde68a', text:'#92400e', badge:'#d97706', badgetxt:'#fff'},
                        good:    {bg:'#f0fdf4', border:'#86efac', text:'#166534', badge:'#16a34a', badgetxt:'#fff'}
                    };
                    const c = colors[matched.level] || colors.warning;
                    bar.style.display = 'block';
                    bar.innerHTML = `
                        <div style="background:${c.bg};border:1.5px solid ${c.border};border-radius:12px;padding:12px 18px;display:flex;align-items:center;gap:12px;flex-wrap:wrap;box-shadow:0 2px 8px rgba(0,0,0,.08);margin-top:8px">
                          <span style="background:${c.badge};color:${c.badgetxt};font-size:10px;font-weight:700;letter-spacing:1px;text-transform:uppercase;padding:3px 10px;border-radius:100px;white-space:nowrap">${matched.risk} RISK</span>
                          <span style="font-size:13px;color:${c.text};font-weight:500;flex:1">${matched.message}</span>
                          <div style="display:flex;gap:6px;flex-shrink:0">
                            <span style="background:rgba(0,0,0,.06);border-radius:8px;padding:4px 10px;font-size:12px;font-weight:600;color:${c.text}">🌡️ ${weatherData.temp}°C</span>
                            <span style="background:rgba(0,0,0,.06);border-radius:8px;padding:4px 10px;font-size:12px;font-weight:600;color:${c.text}">💧 ${weatherData.humidity}%</span>
                            <span style="background:rgba(0,0,0,.06);border-radius:8px;padding:4px 10px;font-size:12px;font-weight:600;color:${c.text}">🌧️ ${weatherData.rain}mm</span>
                          </div>
                          <button onclick="this.closest('div').parentElement.style.display='none'" style="background:rgba(0,0,0,.08);border:none;color:${c.text};cursor:pointer;padding:5px 10px;border-radius:7px;font-size:12px;font-weight:600">Dismiss</button>
                        </div>`;
                }
            } catch(e) {
                showFallbackAlert(bar);
            }
        }, () => showFallbackAlert(bar));

    } catch(e) {
        console.log('Weather fetch failed:', e);
    }
}

function showFallbackAlert(bar) {
    // Show seasonal advice without location
    const month = new Date().getMonth() + 1;
    let msg = '';
    let level = 'warning';

    if (month >= 6 && month <= 9) {
        msg = '🌧️ Monsoon Season: HIGH RISK of fungal diseases. Monitor crops daily. Apply preventive fungicides.';
        level = 'danger';
    } else if (month >= 11 || month <= 2) {
        msg = '❄️ Winter Season: MEDIUM RISK of Wheat Rust and Powdery Mildew. Keep monitoring fields.';
        level = 'warning';
    } else {
        msg = '☀️ Summer Season: Watch for Spider Mites and viral diseases spread by whitefly. Use yellow sticky traps.';
        level = 'warning';
    }

    const levelColors = {
        danger:  {bg:'#fef2f2', border:'#fca5a5', text:'#991b1b', badge:'#dc2626'},
        warning: {bg:'#fffbeb', border:'#fde68a', text:'#92400e', badge:'#d97706'}
    };
    const c = levelColors[level] || levelColors.warning;
    bar.style.display = 'block';
    bar.innerHTML = `
        <div style="background:${c.bg};border:1.5px solid ${c.border};border-radius:12px;padding:12px 18px;display:flex;align-items:center;gap:12px;flex-wrap:wrap;box-shadow:0 2px 8px rgba(0,0,0,.08);margin-top:8px">
          <span style="background:${c.badge};color:#fff;font-size:10px;font-weight:700;letter-spacing:1px;text-transform:uppercase;padding:3px 10px;border-radius:100px;white-space:nowrap">SEASONAL ALERT</span>
          <span style="font-size:13px;color:${c.text};font-weight:500;flex:1">${msg}</span>
          <button onclick="this.closest('div').parentElement.style.display='none'" style="background:rgba(0,0,0,.08);border:none;color:${c.text};cursor:pointer;padding:5px 10px;border-radius:7px;font-size:12px;font-weight:600">Dismiss</button>
        </div>`;
}

// Offline detection
function setupOfflineDetection() {
    const badge = document.getElementById('offlineBadge');
    if (!badge) return;

    function updateOnlineStatus() {
        if (!navigator.onLine) {
            badge.classList.add('show');
        } else {
            badge.classList.remove('show');
        }
    }
    window.addEventListener('online', updateOnlineStatus);
    window.addEventListener('offline', updateOnlineStatus);
    updateOnlineStatus();
}

// PWA Service Worker registration
function registerServiceWorker() {
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/sw.js')
            .then(() => console.log('[PWA] Service Worker registered'))
            .catch(e => console.log('[PWA] SW registration failed:', e));
    }
}

// WhatsApp share function
function shareWhatsApp() {
    const disease  = document.getElementById('resultDisease')?.textContent || 'Unknown';
    const meta     = document.getElementById('resultMeta')?.textContent?.split('·')[0]?.trim() || '';
    const conf     = document.getElementById('confidenceNum')?.textContent || '';
    const severity = document.querySelector('.severity-chip')?.textContent || '';
    const desc     = document.getElementById('diseaseDesc')?.textContent || '';
    const yield_   = document.getElementById('yieldBig')?.textContent || 'N/A';

    const msg =
        `🌿 *AgriLeaf AI Disease Report*\n\n` +
        `🔴 *Disease:* ${disease}\n` +
        `🌱 *Crop:* ${meta}\n` +
        `⚠️ *Severity:* ${severity}\n` +
        `🎯 *Confidence:* ${conf}\n` +
        `📉 *Yield Risk:* ${yield_}\n\n` +
        `📋 *About:* ${desc.substring(0, 200)}...\n\n` +
        `_Detected by AgriLeaf AI — Dept. of AI & ML, Batch A8_\n` +
        `_Visit: http://localhost:5000_`;

    window.open(`https://wa.me/?text=${encodeURIComponent(msg)}`, '_blank');
}

// Init on page load
window.addEventListener('DOMContentLoaded', () => {
    fetchWeatherAndShowAlert();
    setupOfflineDetection();
    registerServiceWorker();
});