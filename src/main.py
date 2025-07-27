import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.models.url import Url
from src.routes.user import user_bp
from src.routes.url import url_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Enable CORS for all routes
CORS(app)

app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(url_bp, url_prefix='/api')

# Add specific route for static files
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(app.static_folder, filename)

# Add specific routes for CSS and JS files
@app.route('/styles.css')
def styles():
    return send_from_directory(app.static_folder, 'styles.css')

@app.route('/script.js')
def script():
    return send_from_directory(app.static_folder, 'script.js')

# Add specific route for short code redirects (before the catch-all route)
@app.route('/<string:short_code>')
def handle_redirect(short_code):
    # Skip if it's a known static file
    if short_code in ['styles.css', 'script.js', 'favicon.ico', 'robots.txt', 'sitemap.xml', 'privacy.html', 'terms.html']:
        return send_from_directory(app.static_folder, short_code)
    
    # Check if it's a short code redirect
    if len(short_code) <= 10 and short_code.isalnum():
        try:
            from src.models.url import Url
            import re
            
            # Validate short code format (alphanumeric only)
            if not re.match(r'^[a-zA-Z0-9]+$', short_code):
                return "Invalid short code format", 400
            
            url_entry = Url.query.filter_by(short_code=short_code).first()
            
            if not url_entry:
                return "Short URL not found", 404
            
            # Increment click count
            url_entry.increment_click_count()
            
            # Redirect to original URL
            from flask import redirect
            return redirect(url_entry.original_url, code=301)
            
        except Exception as e:
            print(f"Error in redirect: {e}")
            return "Internal server error", 500
    else:
        return "Not found", 404

# uncomment if you need to use database
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
with app.app_context():
    db.create_all()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        # Serve index.html for root and unknown paths
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
