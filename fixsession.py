# Run from: C:\Users\nehad\AgriLeaf_Local\agrileaf\
# Command: python fixsession.py

with open('backend/app.py', 'r', encoding='utf-8') as f:
    content = f.read()

import re
lines = content.split('\n')
clean_lines = []
skip_keywords = [
    "SESSION_TYPE", "SESSION_FILE_DIR", "SESSION_PERMANENT",
    "SESSION_COOKIE_SAMESITE", "SESSION_COOKIE_SECURE", "SESSION_COOKIE_HTTPONLY",
    "SESSION_SQLALCHEMY", "PERMANENT_SESSION_LIFETIME", "Session(app)"
]
for line in lines:
    if any(k in line for k in skip_keywords):
        continue
    clean_lines.append(line)

content = '\n'.join(clean_lines)

old_db = "db = SQLAlchemy(app)"
new_db = """db = SQLAlchemy(app)
app.config['SESSION_TYPE'] = 'sqlalchemy'
app.config['SESSION_SQLALCHEMY'] = db
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = 86400 * 7
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
Session(app)"""

content = content.replace(old_db, new_db)

with open('backend/app.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Done!")