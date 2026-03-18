# Run from: C:\Users\nehad\AgriLeaf_Local\agrileaf\
# Command: python fix_mainjs.py

with open('frontend/static/js/main.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Fix 1: renderTreatment - reads wrong field names
old = """        const items =

            type === 'chemical' ? rec.treatment?.chemical || [] :

            type === 'organic'  ? rec.treatment?.organic  || [] :

                                  rec.prevention           || [];"""

new = """        function toArr(v) {
            if (!v) return [];
            if (Array.isArray(v)) return v;
            return v.split('.').map(function(s){ return s.trim(); }).filter(Boolean);
        }
        const items = type === 'chemical' ? toArr(rec.chemical_treatment) :
                      type === 'organic'  ? toArr(rec.organic_treatment)  :
                                           toArr(rec.prevention);"""

if old in js:
    js = js.replace(old, new)
    print("Fix 1 applied: renderTreatment fixed")
else:
    print("Fix 1 FAILED: pattern not found")

# Fix 2: Add predicted_class to analyze trigger
old2 = """renderResults(data);

                setTimeout(loadHistory, 800);"""
new2 = """renderResults(data);

                setTimeout(loadHistory, 800);

                if (data.predicted_class) {
                    fetchFollowupQuestions(data.predicted_class, data.recommendation ? data.recommendation.severity_level : 'moderate');
                }"""

if old2 in js:
    js = js.replace(old2, new2)
    print("Fix 2 applied: followup trigger added")
else:
    print("Fix 2 FAILED: pattern not found")

# Fix 3: Add shareWhatsApp if missing
if 'shareWhatsApp' not in js:
    js += """
function shareWhatsApp() {
    var disease = document.getElementById('resultDisease') ? document.getElementById('resultDisease').textContent : 'Unknown';
    var crop = document.getElementById('resultMeta') ? document.getElementById('resultMeta').textContent.split('·')[0].trim() : '';
    var conf = document.getElementById('confidenceNum') ? document.getElementById('confidenceNum').textContent : '';
    var sevChip = document.querySelector('.severity-chip');
    var severity = sevChip ? sevChip.textContent : '';
    var desc = document.getElementById('diseaseDesc') ? document.getElementById('diseaseDesc').textContent : '';
    var msg = '🌿 *AgriLeaf AI Disease Report*\\n\\n🔴 *Disease:* ' + disease + '\\n🌱 *Crop:* ' + crop + '\\n⚠️ *Severity:* ' + severity + '\\n📊 *Confidence:* ' + conf + '\\n\\n📋 ' + desc.substring(0,200) + '...\\n\\n_Detected by AgriLeaf AI — Dept. of AI & ML, Batch A8_';
    window.open('https://wa.me/?text=' + encodeURIComponent(msg), '_blank');
}
"""
    print("Fix 3 applied: shareWhatsApp added")

# Fix 4: Add fetchFollowupQuestions and submitFollowup if missing
if 'fetchFollowupQuestions' not in js:
    js += """
async function fetchFollowupQuestions(predictedClass, severity) {
    try {
        var res = await fetch('/followup_questions', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({predicted_class:predictedClass})});
        var data = await res.json();
        if (data.has_questions) {
            var card = document.getElementById('followupCard');
            var container = document.getElementById('followupQuestions');
            if (!card || !container) return;
            container.innerHTML = '';
            window._followupAnswers = new Array(data.questions.length).fill(null);
            window._followupClass = predictedClass;
            window._followupSeverity = severity;
            data.questions.forEach(function(q, idx) {
                var div = document.createElement('div');
                div.style.marginBottom = '14px';
                div.innerHTML = '<p style="font-size:13px;font-weight:600;color:#1a3d2b;margin-bottom:8px">' + (idx+1) + '. ' + q.text + '</p>' +
                    q.options.map(function(opt, oi) {
                        return '<label style="display:flex;align-items:center;gap:8px;padding:8px 12px;border:1.5px solid #e5e7eb;border-radius:8px;margin-bottom:6px;cursor:pointer;font-size:13px" onclick="selectAnswer(' + idx + ',' + oi + ',this)">' +
                            '<span style="width:16px;height:16px;border-radius:50%;border:2px solid #9ca3af;flex-shrink:0" id="radio_' + idx + '_' + oi + '"></span>' + opt + '</label>';
                    }).join('');
                container.appendChild(div);
            });
            card.style.display = 'block';
            card.scrollIntoView({behavior:'smooth', block:'nearest'});
        }
    } catch(e) {}
}

function selectAnswer(qIdx, answerIdx, labelEl) {
    window._followupAnswers[qIdx] = answerIdx;
    var radios = document.querySelectorAll('[id^="radio_' + qIdx + '_"]');
    radios.forEach(function(r) { r.style.background=''; r.style.borderColor='#9ca3af'; });
    var sel = document.getElementById('radio_' + qIdx + '_' + answerIdx);
    if (sel) { sel.style.background='#1a3d2b'; sel.style.borderColor='#1a3d2b'; }
    labelEl.parentElement.querySelectorAll('label').forEach(function(l) { l.style.borderColor='#e5e7eb'; l.style.background=''; });
    labelEl.style.borderColor='#2d6a4f';
    labelEl.style.background='#f0fdf4';
}

async function submitFollowup() {
    var answers = window._followupAnswers;
    if (!answers || answers.some(function(a){return a===null;})) { alert('Please answer all questions.'); return; }
    try {
        var res = await fetch('/confirm_diagnosis', {method:'POST', headers:{'Content-Type':'application/json'},
            body:JSON.stringify({predicted_class:window._followupClass, answers:answers, severity:window._followupSeverity})});
        var data = await res.json();
        document.getElementById('followupCard').style.display='none';
        var resultDiv = document.getElementById('confirmResult');
        var msgDiv = document.getElementById('confirmMessage');
        if (!resultDiv || !msgDiv) return;
        var color = data.confirmed ? (data.adjusted_severity==='severe' ? '#dc2626':'#16a34a') : '#f59e0b';
        var bg = data.confirmed ? (data.adjusted_severity==='severe' ? '#fef2f2':'#f0fdf4') : '#fefce8';
        msgDiv.style.cssText = 'font-size:14px;font-weight:600;padding:14px;border-radius:8px;background:'+bg+';color:'+color+';border:1.5px solid '+color;
        msgDiv.innerHTML = '<i class="fas fa-'+(data.confirmed?'check-circle':'exclamation-triangle')+'"></i> '+data.message+
            '<div style="font-size:12px;font-weight:400;margin-top:6px;opacity:.8">Adjusted severity: <strong>'+data.adjusted_severity.toUpperCase()+'</strong></div>';
        resultDiv.style.display='block';
        var chip=document.getElementById('severityChip'); var fill=document.getElementById('severityFill');
        if(chip){chip.textContent=data.adjusted_severity.charAt(0).toUpperCase()+data.adjusted_severity.slice(1); chip.className='severity-chip '+data.adjusted_severity;}
        if(fill) fill.className='severity-bar-fill '+data.adjusted_severity;
    } catch(e) { alert('Error confirming. Try again.'); }
}
"""
    print("Fix 4 applied: followup functions added")

with open('frontend/static/js/main.js', 'w', encoding='utf-8') as f:
    f.write(js)

print("\\nDONE! Restart Flask and refresh browser.")