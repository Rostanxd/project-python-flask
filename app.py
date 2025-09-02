import os
from app import create_app
from app.config import DevelopmentConfig, ProductionConfig

config_class = (
    DevelopmentConfig
    if os.getenv("FLASK_ENV", "development") == "development"
    else ProductionConfig
)
app = create_app(config_class=config_class)

if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_ENV") == "development")
