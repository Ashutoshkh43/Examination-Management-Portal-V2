from flask import Flask
from flask_security import Security, SQLAlchemyUserDatastore, hash_password

from config import Config
from controllers.database import db
from models.models import User, Role


app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

user_datastore = SQLAlchemyUserDatastore(db, User, Role)

security = Security(app, user_datastore)

with app.app_context():

    db.create_all()

    user_datastore.find_or_create_role(
        name='admin',
        description='Administrator'
    )

    user_datastore.find_or_create_role(
        name='examiner',
        description='Examiner'
    )

    user_datastore.find_or_create_role(
        name='student',
        description='Student'
    )

    admin = user_datastore.find_user(
        email=app.config['ADMIN_EMAIL']
    )

    if not admin:
        user_datastore.create_user(
            email=app.config['ADMIN_EMAIL'],
            password=app.config['ADMIN_PASSWORD'],
            roles=['admin']
        )
    db.session.commit()
@app.route('/')
def home():
    return {
        'message': 'Examination Management Portal API is running'
    }
if __name__ == '__main__':
    app.run(debug=True)