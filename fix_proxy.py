# Run from: C:\Users\nehad\AgriLeaf_Local\agrileaf\
# Command: python fix_proxy.py

with open('backend/app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add ProxyFix import
old_import = "from flask import Flask, request, jsonify, render_template, session, redirect, url_for"
new_import = "from flask import Flask, request, jsonify, render_template, session, redirect, url_for\nfrom werkzeug.middleware.proxy_fix import ProxyFix"

content = content.replace(old_import, new_import)

# Add ProxyFix after app creation
old_app = "app = Flask(__name__"
# Find the full app = Flask line
idx = content.find("app = Flask(__name__")
end = content.find("\n", idx)
flask_line = content[idx:end]
new_flask = flask_line + "\napp.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)"

content = content.replace(flask_line, new_flask)

with open('backend/app.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("ProxyFix added!")