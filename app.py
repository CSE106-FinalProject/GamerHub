from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# creating db here to prevent error with working out of scope
with app.app_context():
    db.create_all()


# class Owner(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(20))
#     address = db.Column(db.String(100))
#     pets = db.relationship('Pet', backref='owner')


# class Pet(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(20))
#     age = db.Column(db.Integer)
#     owner_id = db.Column(db.Integer, db.ForeignKey('owner.id'))


class User(db.Model):
    """
    User Database
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(20), unique=True, nullable=False)
    # 1 user to many videos
    video: db.relationship("Video", backref=db.backref('video', lazy=True))

    def __repr__(self):
        return '<User %r>' % self.username


class Video(db.Model):
    #__tablename__ = 'videos'
    id = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.String, unique=True, nullable=False)

    # Many Videos to 1 user
    users_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # user_id = db.Column(db.Integer, db.Foreignkey('user.id'))

    # Many Videos to 1 game tag
    game_tag = db.Column(db.Integer, db.ForeignKey('game.id'))

    def __repr__(self):
        return '<Videos %r>' % self.link


class Profile(db.Model):
    #__tablename__ = 'profiles'
    id = db.Column(db.Integer, primary_key=True)
    bio = db.Column(db.String, unique=False, nullable=True)
    email = db.Column(db.String, unique=True, nullable=True)
    phone_number = db.Column(db.String, unique=True, nullable=True)
    gamer_tag = db.Column(db.String, unique=False, nullable=True)

    # 1 user to 1 profile
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Profile %r>' % self.gamer_tag


class Game(db.Model):
    #__tablename__ = 'games'
    id = db.Column(db.Integer, primary_key=True)
    icons = db.Column(db.String, unique=True, nullable=False)

    # 1 game_icon to many videos
    video = db.relationship("Videos", backref='game')

    def __repr__(self):
        return '<Games %r>' % self.icons


@app.route("/")
def index():
    return "<h1>Hello World!! </h1>"
