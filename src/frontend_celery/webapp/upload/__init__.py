def create_module(app, **kwargs):
    from .upload_routes import upload_blueprint
    app.register_blueprint(upload_blueprint)