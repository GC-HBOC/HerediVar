def create_module(app, **kwargs):
    from .api_routes import api_blueprint
    app.register_blueprint(api_blueprint)