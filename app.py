# IMPORTS
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_qrcode import QRcode
from flask_login import LoginManager, current_user
from functools import wraps
import os

# CONFIG
app = Flask(__name__)
app.config['SECRET_KEY'] = 'LongAndRandomSecretKey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lottery.db'
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['RECAPTCHA_PUBLIC_KEY'] = os.getenv('RECAPTCHA_PUBLIC_KEY')
app.config['RECAPTCHA_PRIVATE_KEY'] = os.getenv('RECAPTCHA_PRIVATE_KEY')

def requires_roles(*roles):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if current_user.role not in roles:
                return forbidden(403)
            return f(*args, **kwargs)
        return wrapped
    return wrapper


# initialise database and QRcode
db = SQLAlchemy(app)
qrcode = QRcode(app)


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
    app.run()
