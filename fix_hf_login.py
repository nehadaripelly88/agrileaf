# Run from: C:\Users\nehad\AgriLeaf_Local\agrileaf\
# Command: python fix_hf_login.py

with open('backend/app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add demo account creation on startup
old = "with app.app_context():\n    db.create_all()\nload_model()"

new = """with app.app_context():
    db.create_all()
    # Create demo account if not exists
    from werkzeug.security import generate_password_hash
    demo = User.query.filter_by(username='demo').first()
    if not demo:
        demo_user = User(
            username='demo',
            email='demo@agrileaf.local',
            password_hash=generate_password_hash('demo123')
        )
        db.session.add(demo_user)
        db.session.commit()
        print('[DB] Demo account created: demo / demo123')
load_model()"""

if old in content:
    content = content.replace(old, new)
    with open('backend/app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Done! Demo account will be created on startup.")
    print("Login with: username=demo, password=demo123")
else:
    print("Pattern not found - check app.py")