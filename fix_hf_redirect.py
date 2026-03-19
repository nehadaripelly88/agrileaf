# Run from: C:\Users\nehad\AgriLeaf_Local\agrileaf\
# Command: python fix_hf_redirect.py

with open('backend/app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix session cookie settings for HTTPS on HF
old = """app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = 86400 * 7"""

new = """app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = 86400 * 7"""

if old in content:
    content = content.replace(old, new)
    print("Session cookie fixed for HTTPS!")
else:
    # Add it fresh
    content = content.replace(
        "app.secret_key = 'agrileaf_secret_key_2024_production_fixed'",
        "app.secret_key = 'agrileaf_secret_key_2024_production_fixed'\napp.config['SESSION_COOKIE_SAMESITE'] = 'None'\napp.config['SESSION_COOKIE_SECURE'] = True\napp.config['SESSION_COOKIE_HTTPONLY'] = True\napp.config['PERMANENT_SESSION_LIFETIME'] = 86400 * 7"
    )
    print("Session cookie added fresh!")

with open('backend/app.py', 'w', encoding='utf-8') as f:
    f.write(content)