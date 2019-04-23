from flask import render_template,current_app,abort,request
import sys
import traceback
from app import db
from app.errors import bp
from app.api.errors import error_response as api_error_response

def wants_json_response():
    return request.accept_mimetypes['application/json'] >=request.accept_mimetypes['text/html']


@bp.app_errorhandler(400)
def not_found_error(error):
    if wants_json_response():
        return api_error_response(400)
    return render_template('errors/404.html'),400

@bp.app_errorhandler(401)
def not_found_error(error):
    if wants_json_response():
        return api_error_response(401)
    return render_template('errors/404.html'),401

# @bp.app_errorhandler(402)
# def not_found_error(error):
#     if wants_json_response():
#         return api_error_response(402)
#     return render_template('errors/404.html'),402

@bp.app_errorhandler(403)
def not_found_error(error):
    if wants_json_response():
        return api_error_response(403)
    return render_template('errors/404.html'),403



@bp.app_errorhandler(404)
def not_found_error(error):
    if wants_json_response():
        return api_error_response(404)
    return render_template('errors/404.html'),404

@bp.app_errorhandler(405)
def not_found_error(error):
    if wants_json_response():
        return api_error_response(405)
    return render_template('errors/404.html'),405
    

@bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()

    current_app.logger.debug("error occurred: %s" % error)
    try:
        code = error.code
        errmsg="error occurred: %s" % error
        # if code == 400:
        #     return render_template('400.html')
        # elif code == 401:
        #     return render_template('401.html')
        # else:
        #     return render_template('error.html')
        etype, value, tb = sys.exc_info()
       # print traceback.print_exception(etype, value, tb)

    except Exception as error:
        current_app.logger.debug('exception is %s' % error)
    finally:
        if wants_json_response():
            return api_error_response(500)
        return render_template('errors/500.html',code=code,msg=errmsg), 500


@bp.route('/testError')
def testError():
    print('testError')
    abort(500)
 