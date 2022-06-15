def create_module(app, **kwargs):
    from .extended_information_routes import extended_information_blueprint
    app.register_blueprint(extended_information_blueprint)