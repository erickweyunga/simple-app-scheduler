from flask import Flask
from app.scheduler.scheduler import init_scheduler
from app.routes.message_routes import message_blueprint
from app.routes.template_routes import template_blueprint
from app.config import Config

def create_app():
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(Config)
    
    # Initialize scheduler
    init_scheduler(app)
    
    # Register blueprints
    app.register_blueprint(message_blueprint)
    app.register_blueprint(template_blueprint)
    
    return app
