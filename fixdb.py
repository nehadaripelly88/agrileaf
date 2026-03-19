with open('backend/app.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = """with app.app_context():
    db.create_all()"""

new = """with app.app_context():
    # Drop and recreate all tables to fix schema issues
    db.drop_all()
    db.create_all()"""

content = content.replace(old, new)

with open('backend/app.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Done!")