# IMPORTS
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_qrcode import QRcode
from flask_login import LoginManager, current_user
from functools import wraps
from flask_talisman import Talisman
import logging, os

# CONFIG
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_ECHO'] = os.getenv('SQLALCHEMY_ECHO')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS')
app.config['RECAPTCHA_PUBLIC_KEY'] = os.getenv('RECAPTCHA_PUBLIC_KEY')
app.config['RECAPTCHA_PRIVATE_KEY'] = os.getenv('RECAPTCHA_PRIVATE_KEY')

# only allows permitted roles to access certain webpages/methods
def requires_roles(*roles):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if current_user.role not in roles:
                logging.warning('SECURITY - Unauthorised Access Denied [%s, %s, %s, %s]',
                                current_user.id,
                                current_user.email,
                                current_user.role,
                                request.remote_addr)
                
                return forbidden(403)
            return f(*args, **kwargs)
        return wrapped
    return wrapper


# create custom content security policy
csp = {
    'default-src': [
        '\'self\'',
        'https://cdnjs.cloudflare.com/ajax/libs/bulma/0.7.2/css/bulma.min.css'
    ],
    'frame-src': [
        '\'self\'',
        'https://www.google.com/recaptcha/',
        'https://recaptcha.google.com/recaptcha/'
    ],
    'script-src': [
        '\'self\'',
        '\'unsafe-inline\'',
        'https://www.google.com/recaptcha/',
        'https://www.gstatic.com/recaptcha/'
    ],
    'img-src': [
        'data:'
    ]
}

# initialise database, talisman and QRcode
db = SQLAlchemy(app)
talisman = Talisman(app, content_security_policy=csp)
qrcode = QRcode(app)

# initialise logger and file handler
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('lottery.log', 'a')
file_handler.setLevel(logging.WARNING)

# filter for logs that include the string 'SECURITY'
class SecurityFilter(logging.Filter):
    
    def filter(self, record):
        return 'SECURITY' in record.getMessage()
    
file_handler.addFilter(SecurityFilter())
formatter = logging.Formatter('%(asctime)s : %(message)s', '%m/%d/%Y %I:%M:%S %p')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# initialise login manager
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    from models import User
    return User.query.get(int(id))

# HOME PAGE VIEW
@app.route('/')
def index():
    return render_template('main/index.html')


# BLUEPRINTS
# import blueprints
from users.views import users_blueprint
from admin.views import admin_blueprint
from lottery.views import lottery_blueprint

# # register blueprints with app
app.register_blueprint(users_blueprint)
app.register_blueprint(admin_blueprint)
app.register_blueprint(lottery_blueprint)


# ERROR HANDLING
@app.errorhandler(400)
def bad_request(error):
    return render_template('errors/error.html', error="Bad Request", text="The server cannot or will not process the request due to something that is perceived to be a client error.",
                           link="https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/400"), 400

@app.errorhandler(403)
def forbidden(error):
    return render_template('errors/error.html', error="Forbidden", text="The client does not have access rights to the content.",
                           link="https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/403"), 403

@app.errorhandler(404)
def not_found(error):
     return render_template('errors/error.html', error="Not Found", text="The server cannot find the requested resource.",
                           link="https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/404"), 404

@app.errorhandler(500)
def internal_server_error(error):
    return render_template('errors/error.html', error="Internal Server Error", text="The server has encountered a situation it does not know how to handle.",
                           link="https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/500"), 500

@app.errorhandler(503)
def service_unavailable(error):
    return render_template('errors/error.html', error="Service Unavailable", text="The server is not ready to handle the request.",
                           link="https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/503"), 503


if __name__ == "__main__":
    #app.run()
    #app.run(ssl_context='adhoc')
    app.run(ssl_context=('cert.pem', 'key.pem'))
