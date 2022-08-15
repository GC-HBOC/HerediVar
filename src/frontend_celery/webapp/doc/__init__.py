def create_module(app, **kwargs):
    from .doc_routes import doc_blueprint
    app.register_blueprint(doc_blueprint)