def create_module(app, **kwargs):
    from .download_routes import download_blueprint
    app.register_blueprint(download_blueprint)