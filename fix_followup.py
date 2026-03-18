# Run from: C:\Users\nehad\AgriLeaf_Local\agrileaf\
# Command: python fix_followup.py

with open('frontend/templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Add followup card before severity block
old = '<div class="severity-block">'
new = """<!-- FOLLOW-UP QUESTIONS -->
                <div class="info-card" id="followupCard" style="display:none;border:2px solid #2d6a4f;background:#f0fdf4">
                    <h4 style="color:#1a3d2b"><i class="fas fa-question-circle"></i> Confirm Your Diagnosis</h4>
                    <p style="font-size:13px;color:#374151;margin-bottom:16px">Answer these quick questions to verify the AI result and adjust severity accurately.</p>
                    <div id="followupQuestions"></div>
                    <button onclick="submitFollowup()" style="background:#1a3d2b;color:#fff;border:none;padding:11px 24px;border-radius:10px;font-size:14px;font-weight:700;cursor:pointer;width:100%;margin-top:12px;font-family:inherit"><i class="fas fa-check"></i> Confirm Diagnosis</button>
                </div>
                <div class="info-card" id="confirmResult" style="display:none">
                    <div id="confirmMessage" style="font-size:14px;font-weight:600;padding:12px;border-radius:8px"></div>
                </div>

                <div class="severity-block">"""

if old in html:
    html = html.replace(old, new, 1)
    with open('frontend/templates/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Done! Follow-up questions UI added.")
else:
    print("Pattern not found")