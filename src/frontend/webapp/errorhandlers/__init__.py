from .errorhandlers import *

def create_module(app, **kwargs):
    
    app.register_error_handler(404, not_found)
    app.register_error_handler(403, forbidden)
    app.register_error_handler(500, internal_server_error)