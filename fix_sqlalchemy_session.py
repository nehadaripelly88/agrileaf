# Run from: C:\Users\nehad\AgriLeaf_Local\agrileaf\
# Command: python fix_sqlalchemy_session.py

with open('backend/app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace filesystem session with sqlalchemy session
old = """app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = '/tmp/flask_sessions'
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = 86400 * 7
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
Session(app)"""

new = """app.config['SESSION_TYPE'] = 'sqlalchemy'
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = 86400 * 7
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True"""

if old in content:
    content = content.replace(old, new)
    print("Session config updated to sqlalchemy!")
else:
    print("Pattern not found")

# Add Session(app) after db = SQLAlchemy(app)
old_db = "db = SQLAlchemy(app)"
new_db = """db = SQLAlchemy(app)
app.config['SESSION_SQLALCHEMY'] = db
Session(app)"""

if old_db in content:
    content = content.replace(old_db, new_db)
    print("Session(app) added after db!")

with open('backend/app.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Done!")