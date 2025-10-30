from webapp.app import app
from config.settings import Config
from ml_model.model_architecture import SentiNN

if __name__ == '__main__':
    print(f"Starting Sentiment Analysis WebApp on port {Config.WEBAPP_PORT}")
    app.run(host='0.0.0.0', port=Config.WEBAPP_PORT, debug=Config.DEBUG)