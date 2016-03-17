import os
from api.views import api_v1_bp
from app import app

app.register_blueprint(api_v1_bp)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port)