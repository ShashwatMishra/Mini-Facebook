from app import db,app
from app.models import User, Post,followers,Message
from flask_login import current_user
shash = User.query.filter_by(username ='Shashwat Mishra').first()
'''suman = User.query.filter_by(username ='Suman').first()
shash.follow(suman)
db.session.commit() '''

data_messages = Message.query.all()
for i in data_messages:
    print(i.text)