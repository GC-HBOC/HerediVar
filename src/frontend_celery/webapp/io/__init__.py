def create_module(app, **kwargs):
    from .download_routes import download_blueprint
    app.register_blueprint(download_blueprint)
    from .variant_io_routes import variant_io_blueprint
    app.register_blueprint(variant_io_blueprint)
    from .task_helper_routes import task_helper_blueprint
    app.register_blueprint(task_helper_blueprint)