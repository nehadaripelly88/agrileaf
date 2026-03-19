# Run from: C:\Users\nehad\AgriLeaf_Local\agrileaf\
# Command: python fix_hf_session.py

with open('backend/app.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = "app.secret_key = 'agrileaf_secret_key_2024'"
new = """app.secret_key = 'agrileaf_secret_key_2024_production_fixed'
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = 86400 * 7"""

if old in content:
    content = content.replace(old, new)
    with open('backend/app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Done! Session config fixed for Hugging Face.")
else:
    print("Pattern not found")