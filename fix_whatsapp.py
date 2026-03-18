# Run from: C:\Users\nehad\AgriLeaf_Local\agrileaf\
# Command: python fix_whatsapp.py

with open('frontend/templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

old = 'onclick="downloadReport()"><i class="fas fa-download"></i> Download Report</button>'
new = 'onclick="downloadReport()"><i class="fas fa-download"></i> Download Report</button>\n                    <button style="background:#25d366;color:#fff;border:none;padding:10px 18px;border-radius:10px;font-size:13px;font-weight:700;cursor:pointer;display:inline-flex;align-items:center;gap:7px;font-family:inherit;margin-left:8px" onclick="shareWhatsApp()"><i class="fab fa-whatsapp"></i> Share on WhatsApp</button>'

if old in html:
    html = html.replace(old, new)
    with open('frontend/templates/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Done! WhatsApp button added.")
else:
    print("Pattern not found - button may already exist or HTML is different")