import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure Secret Key for Sessions
app.secret_key = os.getenv("SECRET_KEY", "your-secret-key")

# Enable CORS (Equivalent to cors({ origin: 'http://localhost:5173', credentials: True }))
CORS(app, origins=["http://localhost:5173"], supports_credentials=True)

# Initialize Database
# Note: Import and call your Python database connection function here (e.g., connect_db())

# Register Blueprints (Equivalent to Express routes)
# from routes.auth_routes import auth_bp
# from routes.assignment_routes import assignment_bp
# from routes.ai_routes import ai_bp
# from routes.gmail_routes import gmail_bp

# app.register_blueprint(auth_bp, url_prefix='/api/auth')
# app.register_blueprint(assignment_bp, url_prefix='/api/assignments')
# app.register_blueprint(ai_bp, url_prefix='/api/ai')
# app.register_blueprint(gmail_bp, url_prefix='/api/gmail')

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)