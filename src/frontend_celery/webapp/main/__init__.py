def create_module(app, **kwargs):
    from .main_routes import main_blueprint
    app.register_blueprint(main_blueprint)