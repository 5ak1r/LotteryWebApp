# do not forget to delete
from app import app, db
from models import User

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