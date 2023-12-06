from app import db, app
from flask_login import UserMixin
from datetime import datetime
#from cryptography.fernet import Fernet
import pyotp, bcrypt, rsa, pickle


'''
Commenting out Symmetric Encryption
def encrypt(data, draw_key):
    return Fernet(draw_key).encrypt(bytes(data, 'utf-8'))


def decrypt(data, draw_key):
    return Fernet(draw_key).decrypt(data).decode('utf-8')
'''

def encrypt(data, public_key):
    return rsa.encrypt(data.encode(), pickle.loads(public_key))

def decrypt(data, private_key):
    return rsa.decrypt(data, pickle.loads(private_key)).decode()

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    # User authentication information.
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    pin_key = db.Column(db.String(32), nullable=False)

    # User information
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.String(100), nullable=False)
    postcode = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=False, default='user')

    # Logging info
    registered_on = db.Column(db.DateTime, nullable=False)
    current_login = db.Column(db.DateTime, nullable=True)
    ip_current = db.Column(db.String(100), nullable=True)
    last_login = db.Column(db.DateTime, nullable=True)
    ip_last = db.Column(db.String(100), nullable=True)
    successful_logins = db.Column(db.Integer, nullable=False)

    # Asymmetric encryption keys
    public_key = db.Column(db.BLOB, nullable=False)
    private_key = db.Column(db.BLOB, nullable=False)
    '''
    # Symmetric encryption key
    draw_key = db.Column(db.BLOB, nullable=False, default=Fernet.generate_key())
    '''

    # Define the relationship to Draw
    draws = db.relationship('Draw')

    def __init__(self, email, firstname, lastname, phone, dob, postcode, password, role):
        self.email = email
        self.firstname = firstname
        self.lastname = lastname
        self.phone = phone
        self.dob = dob
        self.postcode = postcode
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        self.pin_key = pyotp.random_base32()
        self.role = role
        self.registered_on = datetime.now()
        self.current_login = None
        self.ip_current = None
        self.last_login = None
        self.ip_last = None
        self.successful_logins = 0

        # generate unique user asymmetric keys
        public_key, private_key = rsa.newkeys(512)
        self.public_key = pickle.dumps(public_key)
        self.private_key = pickle.dumps(private_key)

    # returns the URI for 2FA
    def get_2fa_uri(self):
        return str(pyotp.totp.TOTP(self.pin_key).provisioning_uri(
            name=self.email)
        )
    
    # returns boolean, True if password entered correctly compared to hashed value in database; False otherwise
    def verify_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password)

    # returns boolean, True if input postcode matches value in database; False otherwise
    def verify_postcode(self, postcode):
        return self.postcode == postcode
    
    # returns boolean, True if input pin matches value in authenticator app; False otherwise
    def verify_pin(self, pin):
        return pyotp.TOTP(self.pin_key).verify(pin)


class Draw(db.Model):
    __tablename__ = 'draws'

    id = db.Column(db.Integer, primary_key=True)

    # ID of user who submitted draw
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)

    # 6 draw numbers submitted
    numbers = db.Column(db.String(100), nullable=False)

    # Draw has already been played (can only play draw once)
    been_played = db.Column(db.BOOLEAN, nullable=False, default=False)

    # Draw matches with master draw created by admin (True = draw is a winner)
    matches_master = db.Column(db.BOOLEAN, nullable=False, default=False)

    # True = draw is master draw created by admin. User draws are matched to master draw
    master_draw = db.Column(db.BOOLEAN, nullable=False)

    # Lottery round that draw is used
    lottery_round = db.Column(db.Integer, nullable=False, default=0)


    '''
    Commenting out Symmetric Encryption
    def __init__(self, user_id, numbers, master_draw, lottery_round, draw_key):
    '''
    def __init__(self, user_id, numbers, master_draw, lottery_round, public_key):
        self.user_id = user_id
        '''
        Commenting out Symmetric Encryption
        self.numbers = encrypt(numbers, draw_key)
        '''
        self.numbers = encrypt(numbers, public_key)
        self.been_played = False
        self.matches_master = False
        self.master_draw = master_draw
        self.lottery_round = lottery_round
        #self.draw_key = draw_key
        self.public_key = public_key


    '''
    Commenting out Symmetric Encryption
    def view_draw(self, draw_key):
        self.numbers = decrypt(self.numbers, draw_key)
    '''
    # decrypts draw numbers but does not save to database
    def view_draw(self, private_key):
        self.numbers = decrypt(self.numbers, private_key)

# reset and reinitialise the database with one admin user
def init_db():
    with app.app_context():
        db.drop_all()
        db.create_all()
        admin = User(email='admin@email.com',
                     password='Admin1!',
                     firstname='Alice',
                     lastname='Jones',
                     phone='0191-123-4567',
                     dob="01/01/1999",
                     postcode="NE1 2AB",
                     role='admin')

        db.session.add(admin)
        db.session.commit()
