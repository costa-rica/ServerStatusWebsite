from flask import Blueprint
from flask import render_template, current_app, request, g
import os
import jinja2
import werkzeug
from app_package._common.utilities import custom_logger, wrap_up_session
from datetime import datetime

logger_bp_error = custom_logger('bp_errors.log')
bp_error = Blueprint('bp_error', __name__)

@bp_error.after_request
def after_request(response):
    logger_bp_error.info(f"---- after_request --- ")
    if hasattr(g, 'db_session'):
        wrap_up_session(logger_bp_error, g.db_session)
    return response


# if os.environ.get('FLASK_CONFIG_TYPE')=='prod':
@bp_error.app_errorhandler(400)
def handle_400(err):
    logger_bp_error.info(f'{err}')
    # logger_bp_error.info(f'- request.referrer: {request.referrer}')
    # logger_bp_error.info(f'- request.url: {request.url}')
    error_message = "Something went wrong. Maybe you entered something I wasn't expecting?"
    return render_template('errors/error_template.html', error_number="400", error_message=error_message)
#messaged copied from: https://www.pingdom.com/blog/the-5-most-common-http-errors-according-to-google/

@bp_error.app_errorhandler(401)
def handle_401(err):
    logger_bp_error.info(f'{err}')

    error_message = "This error happens when a website visitor tries to access a restricted web page but isn’t authorized to do so, usually because of a failed login attempt."
    return render_template('errors/error_template.html', error_number="401", error_message=error_message)
#message copied form: https://www.pingdom.com/blog/the-5-most-common-http-errors-according-to-google/

@bp_error.app_errorhandler(404)
def handle_404(err):
    logger_bp_error.info(f'{err}')
    error_message = "This page doesn't exist. Check what was typed in the address bar."
    return render_template('errors/error_template.html', error_number="404", error_message=error_message, description = err.description)
#404 occurs if address isnt' right

@bp_error.app_errorhandler(500)
def handle_500(err):
    logger_bp_error.info(f'{err}')
    error_message = f"Could be anything... ¯\_(ツ)_/¯  ... try again or send email to {current_app.config['MAIL_USERNAME']}."
    return render_template('errors/error_template.html', error_number="500", error_message=error_message)

@bp_error.app_errorhandler(502)
def handle_502(err):
    logger_bp_error.info(f'{err}')
    error_message = f"Could be anything... ¯\_(ツ)_/¯  ... try again or send email to {current_app.config['MAIL_USERNAME']}."
    return render_template('errors/error_template.html', error_number="502", error_message=error_message)

@bp_error.app_errorhandler(NameError)
@bp_error.app_errorhandler(Exception)
def handle_exception(e):
    # Log the error as you do with other errors
    logger_bp_error.error(f'Unhandled Exception: {e}', exc_info=True)

    # You can check if the error is an HTTPException and use its code
    # Otherwise, use 500 by default for unknown exceptions
    if isinstance(e, werkzeug.exceptions.HTTPException):
        error_code = e.code
    else:
        error_code = 500
    error_type = type(e).__name__
    error_message = "An unexpected error occurred. We're working to fix the issue."
    error_message = e
    # Return your custom error template and the status code
    return render_template('errors/error_template.html', error_code=error_code,error_type=error_type, 
        error_message=error_message), error_code

