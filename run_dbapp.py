from dbapp.app import app
from config.settings import Config

if __name__ == '__main__':
    print(f"Starting Database API on port {Config.DBAPP_PORT}")
    app.run(host='0.0.0.0', port=Config.DBAPP_PORT, debug=Config.DEBUG)