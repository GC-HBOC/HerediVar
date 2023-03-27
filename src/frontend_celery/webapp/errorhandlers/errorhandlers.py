from flask import Flask, render_template, current_app
import traceback

def not_found(e):
    return render_template('errorhandlers/404.html'), 404

def forbidden(e):
    return render_template('errorhandlers/403.html'), 403

def internal_server_error(e):
    original = getattr(e, "original_exception", None)

    #current_app.logger.exception(e)

    if original is None:
        # triggered if abort(500) is called
        return render_template("errorhandlers/500_unhandled.html", e=e), 500

    # all other unhandled errors
    return render_template("errorhandlers/500_unhandled.html", e=original), 500