from flask import render_template, current_app
import traceback

# These routes are called when flask's abort function is invoked

def not_found(e):
    return render_template('errorhandlers/404.html'), 404

def forbidden(e):
    return render_template('errorhandlers/403.html'), 403

def internal_server_error(e):
    original = getattr(e, "original_exception", None) # original != None: unhandled exception

    if original is None:
        # triggered if abort(500) is called
        original = e

    return render_template("errorhandlers/500_unhandled.html", e=original), 500