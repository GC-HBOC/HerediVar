def create_module(app, **kwargs):
    from .variant_routes import variant_blueprint
    
    app.register_blueprint(variant_blueprint)