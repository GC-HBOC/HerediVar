def create_module(app, **kwargs):
    from .user_routes import user_blueprint
    app.register_blueprint(user_blueprint)