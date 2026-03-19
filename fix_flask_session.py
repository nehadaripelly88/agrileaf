# Run from: C:\Users\nehad\AgriLeaf_Local\agrileaf\
# Command: python fix_flask_session.py

with open('backend/app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add flask-session import
old_import = "from flask import Flask, request, jsonify, render_template, session, redirect, url_for"
new_import = "from flask import Flask, request, jsonify, render_template, session, redirect, url_for\nfrom flask_session import Session"

if old_import in content:
    content = content.replace(old_import, new_import)
    print("Import added!")

# Add server-side session config after secret key
old_config = "app.config['SESSION_COOKIE_SAMESITE'] = 'None'\napp.config['SESSION_COOKIE_SECURE'] = True\napp.config['SESSION_COOKIE_HTTPONLY'] = True\napp.config['PERMANENT_SESSION_LIFETIME'] = 86400 * 7"

new_config = """app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = '/tmp/flask_sessions'
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = 86400 * 7
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
Session(app)"""

if old_config in content:
    content = content.replace(old_config, new_config)
    print("Session config updated!")
else:
    # Add after secret key line
    content = content.replace(
        "app.secret_key = 'agrileaf_secret_key_2024_production_fixed'",
        "app.secret_key = 'agrileaf_secret_key_2024_production_fixed'\napp.config['SESSION_TYPE'] = 'filesystem'\napp.config['SESSION_FILE_DIR'] = '/tmp/flask_sessions'\napp.config['SESSION_PERMANENT'] = True\napp.config['PERMANENT_SESSION_LIFETIME'] = 86400 * 7\nSession(app)"
    )
    print("Session config added fresh!")

with open('backend/app.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Done!")