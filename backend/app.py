from flask import Flask
from flask_cors import CORS
import os
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app)

    # Configuration
    app.config['MODEL_PATH'] = os.getenv('MODEL_PATH', './models/fine_tuned_bert')
    app.config['RASA_ENDPOINT'] = os.getenv('RASA_ENDPOINT', 'http://localhost:5005')
    app.config['MAX_TEXT_LENGTH'] = int(os.getenv('MAX_TEXT_LENGTH', '10000'))
    app.config['MIN_TEXT_LENGTH'] = int(os.getenv('MIN_TEXT_LENGTH', '50'))

    # Register blueprints
    from app.api.nlp_routes import nlp_bp
    from app.api.diagram_routes import diagram_bp

    app.register_blueprint(nlp_bp, url_prefix='/api')
    app.register_blueprint(diagram_bp, url_prefix='/api')

    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'message': 'UML Generator API is running'}

    # Serve frontend static files in production
    if os.getenv('FLASK_ENV') == 'production':
        app.static_folder = '../frontend/build'

        @app.route('/', defaults={'path': ''})
        @app.route('/<path:path>')
        def serve_react_app(path):
            if path == "":
                return app.send_static_file('index.html')
            return app.send_from_directory(app.static_folder, path)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=int(os.getenv('PORT', 5000)))