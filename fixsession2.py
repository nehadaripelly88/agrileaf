with open('backend/app.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = """app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False"""

new = """app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE'] = True"""

if old in content:
    content = content.replace(old, new)
    print("Fixed!")
else:
    print("Not found")

with open('backend/app.py', 'w', encoding='utf-8') as f:
    f.write(content)