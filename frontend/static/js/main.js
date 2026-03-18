/**

 * AgriLeaf — main.js

 * Session-based auth version. No localStorage userId.

 * Backend reads session['username'] automatically.

 */



document.addEventListener('DOMContentLoaded', () => {



    const dropzone  = document.getElementById('dropzone');

    const fileInput = document.getElementById('fileInput');

    const dzIdle    = document.getElementById('dzIdle');

    const dzPreview = document.getElementById('dzPreview');

    const previewImg= document.getElementById('previewImg');

    const removeBtn = document.getElementById('removeBtn');

    const analyzeBtn= document.getElementById('analyzeBtn');

    const cropType  = document.getElementById('cropType');



    let selectedFile = null;

    let currentData  = null;



    checkModelStatus();



    async function checkModelStatus() {

        try {

            const res  = await fetch('/model_status');

            const data = await res.json();

            const dot  = document.getElementById('badgeDot');

            const text = document.getElementById('badgeText');

            if (data.model_loaded) {

                dot.classList.add('live');

                text.textContent = `CNN Active · ${data.num_classes} classes`;

            } else {

                dot.classList.add('demo');

                text.textContent = 'Demo Mode (no trained model)';

            }

        } catch (e) {

            document.getElementById('badgeText').textContent = 'Server not reachable';

        }

    }



    dropzone.addEventListener('click', () => { if (!selectedFile) fileInput.click(); });

    fileInput.addEventListener('change', e => { if (e.target.files[0]) handleFile(e.target.files[0]); });

    dropzone.addEventListener('dragover', e => { e.preventDefault(); dropzone.classList.add('over'); });

    dropzone.addEventListener('dragleave', () => dropzone.classList.remove('over'));

    dropzone.addEventListener('drop', e => {

        e.preventDefault(); dropzone.classList.remove('over');

        if (e.dataTransfer.files[0]) handleFile(e.dataTransfer.files[0]);

    });

    removeBtn.addEventListener('click', e => { e.stopPropagation(); clearFile(); });



    function handleFile(file) {

        if (!['image/jpeg','image/png','image/webp'].includes(file.type)) {

            alert('Please upload a JPG, PNG, or WEBP image.'); return;

        }

        if (file.size > 16 * 1024 * 1024) { alert('File too large. Maximum 16MB.'); return; }

        selectedFile = file;

        const reader = new FileReader();

        reader.onload = e => {

            previewImg.src = e.target.result;

            dzIdle.style.display = 'none';

            dzPreview.style.display = 'block';

        };

        reader.readAsDataURL(file);

        analyzeBtn.disabled = false;

    }



    function clearFile() {

        selectedFile = null; fileInput.value = ''; previewImg.src = '';

        dzPreview.style.display = 'none'; dzIdle.style.display = 'block';

        analyzeBtn.disabled = true; showPanel('rsEmpty');

    }



    analyzeBtn.addEventListener('click', runAnalysis);



    async function runAnalysis() {

        if (!selectedFile) return;

        showPanel('rsLoading'); animateLoadingSteps();

        analyzeBtn.disabled = true;

        analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';

        try {

            const formData = new FormData();

            formData.append('image', selectedFile);

            formData.append('crop_type', cropType.value);

            formData.append('soil_ph', document.getElementById('soilPh')?.value || '');

            formData.append('nitrogen_level', document.getElementById('nitrogenLevel')?.value || '');



            const response = await fetch('/analyze', { method: 'POST', body: formData });

            const data = await response.json();

            if (data.success) {

                currentData = data;

                renderResults(data);

                setTimeout(loadHistory, 800);

                if (data.predicted_class) {
                    fetchFollowupQuestions(data.predicted_class, data.recommendation ? data.recommendation.severity_level : 'moderate');
                }

                if (data.predicted_class) { fetchFollowupQuestions(data.predicted_class, data.recommendation ? data.recommendation.severity_level : 'moderate'); }

            } else {

                showError(data.error || 'Analysis failed.');

            }

        } catch (err) {

            showError('Cannot reach server. Make sure Flask is running.');

        } finally {

            analyzeBtn.disabled = false;

            analyzeBtn.innerHTML = '<i class="fas fa-microscope"></i> Analyze Leaf';

        }

    }



    function renderResults(data) {

        const rec = data.recommendation;

        const severity = rec.severity_level;

        const isHealthy = data.is_healthy;

        const topPreds = data.top_predictions || [];



        document.getElementById('resultEmoji').textContent   = isHealthy ? '✅' : '🔴';

        document.getElementById('resultDisease').textContent = rec.disease;

        document.getElementById('resultMeta').textContent    = `${rec.crop} · ${rec.pathogen}`;

        document.getElementById('confidenceNum').textContent = `${data.confidence}%`;

        document.getElementById('resultHeader').className    = `result-header ${isHealthy ? 'healthy-header' : 'disease-header'}`;



        const predList = document.getElementById('predList');

        predList.innerHTML = '';

        topPreds.forEach((p, i) => {

            const item = document.createElement('div');

            item.className = 'pred-item';

            item.innerHTML = `

                <span class="pred-name">${i+1}. ${p.class.replace(/___/g,' → ').replace(/_/g,' ')}</span>

                <div class="pred-bar-wrap"><div class="pred-bar" style="width:0%" data-width="${p.confidence}%"></div></div>

                <span class="pred-pct">${p.confidence}%</span>`;

            predList.appendChild(item);

        });

        document.getElementById('modelUsed').textContent = `Using: ${data.model_used}`;

        setTimeout(() => {

            document.querySelectorAll('.pred-bar').forEach(b => b.style.width = b.dataset.width);

        }, 100);



        const fillClass = isHealthy ? 'healthy' : severity;

        document.getElementById('severityFill').className = `severity-bar-fill ${fillClass}`;

        const chip = document.getElementById('severityChip');

        chip.textContent = isHealthy ? 'Healthy' : capitalize(severity);

        chip.className = `severity-chip ${fillClass}`;

        document.getElementById('severityDesc').textContent = rec.severity_description || '';



        document.getElementById('diseaseDesc').textContent = rec.description;

        const tagContainer = document.getElementById('symptomTags');

        tagContainer.innerHTML = '';

        (rec.symptoms || []).forEach(s => {

            const t = document.createElement('span');

            t.className = 'stag'; t.textContent = s;

            tagContainer.appendChild(t);

        });



        window._currentRec = rec;

        renderTreatment('chemical');



        const yieldCard = document.getElementById('yieldCard');

        yieldCard.style.display = isHealthy ? 'none' : 'block';

        if (!isHealthy) document.getElementById('yieldBig').textContent = rec.yield_impact || 'N/A';



        renderSoilResults(data.soil_analysis);



        showPanel('rsResults');

        if (window.innerWidth < 900)

            document.getElementById('resultsPanel').scrollIntoView({ behavior: 'smooth' });

    }



    function renderSoilResults(soil) {

        const card = document.getElementById('soilResultCard');

        if (!soil || !soil.has_soil_data) { card.style.display = 'none'; return; }

        card.style.display = 'block';

        card.className = `info-card soil-result-card ${soil.soil_status}`;



        const statusIcons = { good: '✅', moderate: '⚠️', poor: '🔴' };

        document.getElementById('soilStatusRow').innerHTML =

            `<span class="soil-status-chip ${soil.soil_status}">${statusIcons[soil.soil_status]} Soil: ${capitalize(soil.soil_status)}</span>

             ${soil.ph_value !== null ? `<span style="font-size:12px;color:#6b7280">pH ${soil.ph_value}</span>` : ''}

             ${soil.nitrogen ? `<span style="font-size:12px;color:#6b7280">Nitrogen: ${capitalize(soil.nitrogen)}</span>` : ''}`;



        document.getElementById('soilSummary').textContent = soil.summary;



        const warnDiv = document.getElementById('soilWarnings');

        warnDiv.innerHTML = '';

        (soil.warnings || []).forEach(w => {

            const d = document.createElement('div');

            d.className = 'soil-warning-item'; d.textContent = w;

            warnDiv.appendChild(d);

        });



        const advDiv = document.getElementById('soilAdvice');

        advDiv.innerHTML = '';

        (soil.advice || []).forEach(a => {

            const d = document.createElement('div');

            d.className = 'soil-advice-item'; d.textContent = a;

            advDiv.appendChild(d);

        });

    }



    window._renderTreatment = type => renderTreatment(type);



    function renderTreatment(type) {

        const rec = window._currentRec;

        if (!rec) return;

        const list = document.getElementById('treatList');

        const timingNote = document.getElementById('timingNote');

        list.innerHTML = '';

        function toArr(v) {
            if (!v) return [];
            if (Array.isArray(v)) return v;
            return v.split('.').map(function(s){ return s.trim(); }).filter(Boolean);
        }
        const items = type === 'chemical' ? toArr(rec.chemical_treatment) :
                      type === 'organic'  ? toArr(rec.organic_treatment)  :
                                           toArr(rec.prevention);

        if (!items.length) {

            list.innerHTML = '<li>No specific items for this category.</li>';

        } else {

            items.forEach(item => {

                const li = document.createElement('li');

                li.textContent = item; list.appendChild(li);

            });

        }

        if (type !== 'prevention' && rec.treatment?.timing) {

            timingNote.style.display = 'flex';

            timingNote.innerHTML = `<i class="fas fa-clock"></i> <span>${rec.treatment.timing}</span>`;

        } else {

            timingNote.style.display = 'none';

        }

    }



    function animateLoadingSteps() {

        const steps = ['ls1','ls2','ls3','ls4'];

        let i = 0;

        steps.forEach(id => {

            const el = document.getElementById(id);

            el.className = 'ls pending';

            el.querySelector('i').className = 'fas fa-circle';

        });

        document.getElementById(steps[0]).className = 'ls';

        document.getElementById(steps[0]).querySelector('i').className = 'fas fa-circle-notch fa-spin';

        const interval = setInterval(() => {

            if (i < steps.length) {

                if (i > 0) {

                    const prev = document.getElementById(steps[i-1]);

                    prev.className = 'ls done';

                    prev.querySelector('i').className = 'fas fa-check-circle';

                }

                const cur = document.getElementById(steps[i]);

                cur.className = 'ls';

                cur.querySelector('i').className = 'fas fa-circle-notch fa-spin';

                i++;

            } else { clearInterval(interval); }

        }, 700);

    }



    function showPanel(id) {

        ['rsEmpty','rsLoading','rsResults','rsError'].forEach(pid => {

            const el = document.getElementById(pid);

            if (el) el.style.display = pid === id ? 'block' : 'none';

        });

    }



    function showError(msg) {

        document.getElementById('errorMsg').textContent = msg;

        showPanel('rsError');

    }



    window.resetAnalyzer = function() {

        clearFile(); showPanel('rsEmpty');

        document.getElementById('analyzer').scrollIntoView({ behavior: 'smooth' });

    };



    loadHistory();



}); // End DOMContentLoaded





function switchTab(type, btn) {

    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));

    btn.classList.add('active');

    if (window._renderTreatment) window._renderTreatment(type);

}



async function loadHistory() {

    const container = document.getElementById('historyContainer');

    if (!container) return;

    container.innerHTML = '<div class="history-placeholder"><i class="fas fa-spinner fa-spin"></i> Loading...</div>';

    try {

        const res  = await fetch('/history');

        const data = await res.json();

        if (!data.success || !data.history || !data.history.length) {

            container.innerHTML = '<div class="history-placeholder">No analyses yet. Upload your first leaf image!</div>';

            document.getElementById('historyStats').style.display = 'none';

            return;

        }

        document.getElementById('historyStats').style.display = 'flex';

        document.getElementById('hsTotalLabel').textContent   = data.total;

        document.getElementById('hsHealthyLabel').textContent = data.healthy_count;

        document.getElementById('hsDiseaseLabel').textContent = data.diseased_count;



        const grid = document.createElement('div');

        grid.className = 'history-cards';

        data.history.forEach(item => {

            const card = document.createElement('div');

            card.className = 'hcard';

            card.innerHTML = `

                <div class="hcard-top">

                    <div>

                        <div class="hcard-disease">${item.is_healthy ? '✅' : '🔴'} ${item.disease}</div>

                        <div class="hcard-crop">${item.crop}</div>

                    </div>

                    <span class="severity-chip ${item.severity}">${capitalize(item.severity)}</span>

                </div>

                <div class="hcard-bottom">

                    <span>Confidence: ${item.confidence}%</span>

                    <span>${item.date} ${item.time || ''}</span>

                </div>`;

            grid.appendChild(card);

        });

        container.innerHTML = '';

        container.appendChild(grid);

    } catch (err) {

        container.innerHTML = '<div class="history-placeholder">Error loading history.</div>';

    }

}



async function clearHistory() {

    if (!confirm('Clear all your history? This cannot be undone.')) return;

    try {

        const res  = await fetch('/history/clear', { method: 'DELETE' });

        const data = await res.json();

        if (data.success) {

            document.getElementById('historyContainer').innerHTML =

                '<div class="history-placeholder">History cleared.</div>';

            document.getElementById('historyStats').style.display = 'none';

        }

    } catch(e) { alert('Failed to clear history.'); }

}



function downloadReport() {
    var disease  = document.getElementById('resultDisease') ? document.getElementById('resultDisease').textContent : 'Unknown';
    var meta     = document.getElementById('resultMeta') ? document.getElementById('resultMeta').textContent : '';
    var conf     = document.getElementById('confidenceNum') ? document.getElementById('confidenceNum').textContent : '';
    var sevChip  = document.querySelector('.severity-chip');
    var severity = sevChip ? sevChip.textContent : '';
    var desc     = document.getElementById('diseaseDesc') ? document.getElementById('diseaseDesc').textContent : '';
    var treat    = document.getElementById('treatList') ? document.getElementById('treatList').innerText : '';
    var now      = new Date().toLocaleString('en-IN');

    var html = '<!DOCTYPE html><html><head><meta charset="UTF-8"><title>AgriLeaf Report</title>' +
        '<style>body{font-family:Georgia,serif;max-width:700px;margin:40px auto;color:#1a1a1a;padding:0 20px}' +
        '.header{background:#1a3d2b;color:#fff;padding:28px 32px;border-radius:12px;margin-bottom:28px}' +
        '.header h1{margin:0;font-size:22px}.header p{margin:6px 0 0;opacity:.75;font-size:13px}' +
        '.badge{display:inline-block;background:rgba(255,255,255,.15);padding:4px 12px;border-radius:20px;font-size:12px;margin-top:10px}' +
        '.section{margin-bottom:24px;padding:20px 24px;border:1.5px solid #e5e7eb;border-radius:10px}' +
        '.section h3{margin:0 0 12px;font-size:13px;text-transform:uppercase;letter-spacing:1px;color:#2d6a4f}' +
        '.row{display:flex;justify-content:space-between;margin-bottom:8px;font-size:14px}' +
        '.label{color:#6b7280;font-weight:600}.value{font-weight:700}' +
        '.desc{font-size:14px;line-height:1.7;color:#374151;white-space:pre-wrap}' +
        '.footer{text-align:center;font-size:11px;color:#9ca3af;margin-top:32px;padding-top:16px;border-top:1px solid #e5e7eb}' +
        '@media print{body{margin:0}.no-print{display:none}}' +
        '</style></head><body>' +
        '<div class="header"><h1>AgriLeaf Disease Report</h1><p>AI-powered leaf disease analysis</p>' +
        '<span class="badge">Dept. of AI &amp; ML - Batch A8</span></div>' +
        '<div class="section"><h3>Diagnosis</h3>' +
        '<div class="row"><span class="label">Disease</span><span class="value">' + disease + '</span></div>' +
        '<div class="row"><span class="label">Crop / Pathogen</span><span class="value">' + meta + '</span></div>' +
        '<div class="row"><span class="label">Severity</span><span class="value">' + severity + '</span></div>' +
        '<div class="row"><span class="label">Confidence</span><span class="value">' + conf + '</span></div>' +
        '<div class="row"><span class="label">Scan Date</span><span class="value">' + now + '</span></div></div>' +
        '<div class="section"><h3>About this Disease</h3><p class="desc">' + desc + '</p></div>' +
        '<div class="section"><h3>Treatment</h3><p class="desc">' + (treat || 'See treatment tab in app.') + '</p></div>' +
        '<div class="footer no-print"><button onclick="window.print()" style="background:#1a3d2b;color:#fff;border:none;padding:10px 24px;border-radius:8px;font-size:14px;cursor:pointer;margin-bottom:12px">Print / Save as PDF</button><br>' +
        'Generated by AgriLeaf AI - D.Neha, D.Abhishikth, Y.Namitha, G.Meghana<br>' +
        'This report is for guidance only. Consult a local agronomist for severe cases.</div>' +
        '</body></html>';

    var blob = new Blob([html], {type: 'text/html'});
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.href = url;
    a.download = 'AgriLeaf_Report_' + Date.now() + '.html';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}


function capitalize(str) {

    return str ? str.charAt(0).toUpperCase() + str.slice(1) : '';

}



function toggleSoil() {

    const body   = document.getElementById('soilBody');

    const header = body.previousElementSibling;

    const isOpen = body.style.display !== 'none';

    body.style.display = isOpen ? 'none' : 'block';

    header.classList.toggle('open', !isOpen);

}



function updatePhBar() {

    const val    = parseFloat(document.getElementById('soilPh').value);

    const marker = document.getElementById('phMarker');

    if (isNaN(val) || val < 0 || val > 14) { marker.style.display = 'none'; return; }

    marker.style.display = 'block';

    marker.style.left    = (val / 14 * 100) + '%';

}
async function fetchFollowupQuestions(predictedClass, severity) {
    try {
        var res = await fetch('/followup_questions', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({predicted_class: predictedClass})
        });
        var data = await res.json();
        if (data.has_questions) {
            var card = document.getElementById('followupCard');
            var container = document.getElementById('followupQuestions');
            container.innerHTML = '';
            window._followupAnswers = new Array(data.questions.length).fill(null);
            window._followupClass = predictedClass;
            window._followupSeverity = severity;
            data.questions.forEach(function(q, idx) {
                var div = document.createElement('div');
                div.style.cssText = 'margin-bottom:14px';
                div.innerHTML = '<p style="font-size:13px;font-weight:600;color:#1a3d2b;margin-bottom:8px">' + (idx+1) + '. ' + q.text + '</p>' +
                    q.options.map(function(opt, oi) {
                        return '<label style="display:flex;align-items:center;gap:8px;padding:8px 12px;border:1.5px solid #e5e7eb;border-radius:8px;margin-bottom:6px;cursor:pointer;font-size:13px;transition:all .15s" onclick="selectAnswer(' + idx + ',' + oi + ',this)">' +
                            '<span style="width:16px;height:16px;border-radius:50%;border:2px solid #9ca3af;flex-shrink:0" id="radio_' + idx + '_' + oi + '"></span>' +
                            opt + '</label>';
                    }).join('');
                container.appendChild(div);
            });
            card.style.display = 'block';
            document.getElementById('confirmResult').style.display = 'none';
            card.scrollIntoView({behavior: 'smooth', block: 'nearest'});
        }
    } catch(e) {
        console.log('No follow-up questions:', e);
    }
}
 
function selectAnswer(qIdx, answerIdx, labelEl) {
    window._followupAnswers[qIdx] = answerIdx;
    // Update radio visual
    var radios = document.querySelectorAll('[id^="radio_' + qIdx + '_"]');
    radios.forEach(function(r) { r.style.background = ''; r.style.borderColor = '#9ca3af'; });
    var selected = document.getElementById('radio_' + qIdx + '_' + answerIdx);
    if (selected) { selected.style.background = '#1a3d2b'; selected.style.borderColor = '#1a3d2b'; }
    // Highlight selected label
    labelEl.parentElement.querySelectorAll('label').forEach(function(l) { l.style.borderColor = '#e5e7eb'; l.style.background = ''; });
    labelEl.style.borderColor = '#2d6a4f';
    labelEl.style.background = '#f0fdf4';
}
 
async function submitFollowup() {
    var answers = window._followupAnswers;
    if (answers.some(function(a) { return a === null; })) {
        alert('Please answer all questions before confirming.');
        return;
    }
    try {
        var res = await fetch('/confirm_diagnosis', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                predicted_class: window._followupClass,
                answers: answers,
                severity: window._followupSeverity
            })
        });
        var data = await res.json();
        document.getElementById('followupCard').style.display = 'none';
        var resultDiv = document.getElementById('confirmResult');
        var msgDiv = document.getElementById('confirmMessage');
        var color = data.confirmed ? (data.adjusted_severity === 'severe' ? '#dc2626' : '#16a34a') : '#f59e0b';
        var bg = data.confirmed ? (data.adjusted_severity === 'severe' ? '#fef2f2' : '#f0fdf4') : '#fefce8';
        msgDiv.style.cssText = 'font-size:14px;font-weight:600;padding:14px;border-radius:8px;background:' + bg + ';color:' + color + ';border:1.5px solid ' + color;
        msgDiv.innerHTML = '<i class="fas fa-' + (data.confirmed ? 'check-circle' : 'exclamation-triangle') + '"></i> ' + data.message +
            '<div style="font-size:12px;font-weight:400;margin-top:6px;opacity:.8">Adjusted severity: <strong>' + data.adjusted_severity.toUpperCase() + '</strong></div>';
        resultDiv.style.display = 'block';
 
        // Update severity chip on main result
        var chip = document.getElementById('severityChip');
        var fill = document.getElementById('severityFill');
        if (chip) { chip.textContent = data.adjusted_severity.charAt(0).toUpperCase() + data.adjusted_severity.slice(1); chip.className = 'severity-chip ' + data.adjusted_severity; }
        if (fill) fill.className = 'severity-bar-fill ' + data.adjusted_severity;
 
        resultDiv.scrollIntoView({behavior: 'smooth', block: 'nearest'});
    } catch(e) {
        alert('Error confirming diagnosis. Please try again.');
    }
}
function shareWhatsApp() {
    var disease = document.getElementById('resultDisease') ? document.getElementById('resultDisease').textContent : 'Unknown';
    var crop = document.getElementById('resultMeta') ? document.getElementById('resultMeta').textContent.split('·')[0].trim() : '';
    var conf = document.getElementById('confidenceNum') ? document.getElementById('confidenceNum').textContent : '';
    var sevChip = document.querySelector('.severity-chip');
    var severity = sevChip ? sevChip.textContent : '';
    var desc = document.getElementById('diseaseDesc') ? document.getElementById('diseaseDesc').textContent : '';
    var msg = '🌿 *AgriLeaf AI Disease Report*\n\n🔴 *Disease:* ' + disease + '\n🌱 *Crop:* ' + crop + '\n⚠️ *Severity:* ' + severity + '\n📊 *Confidence:* ' + conf + '\n\n📋 ' + desc.substring(0,200) + '...\n\n_Detected by AgriLeaf AI — Dept. of AI & ML, Batch A8_';
    window.open('https://wa.me/?text=' + encodeURIComponent(msg), '_blank');
}
