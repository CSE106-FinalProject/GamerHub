from flask import Flask, render_template, url_for, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'thisisasecretkey'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# creating db here to prevent error with working out of scope
with app.app_context():
    db.create_all()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
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
    # __tablename__ = 'videos'
    id = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.String, unique=True, nullable=False)

    # Many Videos to 1 user
    users_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Many Videos to 1 game tag
    game_tag = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=True)

    def __repr__(self):
        return '<Videos %r>' % self.link

    def newVideo(user, url, game):
        video = Video(link=url, users_id=user, game_tag=game)
        db.session.add(video)
        db.session.commit()


class Profile(db.Model):
    # __tablename__ = 'profiles'
    id = db.Column(db.Integer, primary_key=True)
    bio = db.Column(db.String, unique=False, nullable=True)
    email = db.Column(db.String, unique=True, nullable=True)
    phone_number = db.Column(db.String, unique=True, nullable=True)
    gamer_tag = db.Column(db.String, unique=False, nullable=True)

    # 1 user to 1 profile
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Profile %r>' % self.gamer_tag

    def newuserprofile(user):
        profile = Profile(bio=None, email=None,
                          phone_number=None, gamer_tag=None, user_id=user)
        db.session.add(profile)
        db.session.commit()


class Game(db.Model):
    # __tablename__ = 'games'
    id = db.Column(db.Integer, primary_key=True)
    icons = db.Column(db.String, unique=True, nullable=False)

    # 1 game_icon to many videos
    video = db.relationship("Video", backref='game')

    def __repr__(self):
        return '<Games %r>' % self.icons


class RegisterForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                'That username already exists. Please choose a different one.')


class LoginForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')


@app.route('/')
def home():
    return render_template('landing.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('dashboard'))
    return render_template('login.html', form=form)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@ app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        Profile.newuserprofile(new_user.id)
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


# when a user click the profile icon
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = current_user.id
    user_username = current_user.username
    user_profile = Profile.query.filter_by(user_id=user).first()
    user_name = User.query.filter_by(username=user_username).first()

    if request.method == 'POST':
        bio = request.form['bio']
        user_profile.bio = bio

        email = request.form['email']
        user_profile.email = email

        number = request.form['number']
        user_profile.phone_number = number

        tag = request.form['tag']
        user_profile.gamer_tag = tag

        db.session.commit()
        return render_template('profile.html', user=user_name, profile=user_profile)

    return render_template('profile.html', profile=user_profile, user=user_name)


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    user = current_user.username
    user_name = User.query.filter_by(username=user).first()
    video_list = Video.query.with_entities(Video.link).all()
    gametag_list = Video.query.with_entities(Video.game_tag).all()
    user_list = Video.query.with_entities(Video.users_id).all()
    usernameid_list = []
    username_list = []
    for item in user_list:
        temp = str(item).split(",")
        temp2 = temp[0].split("(")
        usernameid_list.append(temp2[1])
    for x in usernameid_list:
        myname = User.query.filter_by(id=x).first()
        username_list.append(myname.username)

    gametagidlist = []
    for item1 in gametag_list:
        temp3 = str(item1).split(",")
        temp4 = temp3[0].split("(")
        gametagidlist.append(temp4[1])

    finalvideo_list = []
    for item2 in video_list:
        temp5 = str(item2).split("'")
        finalvideo_list.append(temp5[1])

    return render_template('dashboard.html', user=user_name, finalvideo_list=finalvideo_list, user_list=user_list, username_list=username_list, gametagidlist=gametagidlist)


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    print("in upload video endpoint")
    if request.method == 'POST':
        uploadURL = request.form['videoURL']
        # user = current_user.username
        # user_name = User.query.filter_by(username=user).first()
        game = request.form['game']
        Video.newVideo(current_user.id, uploadURL, game)

        return redirect(url_for("dashboard"))
    return render_template('videoUpload.html')


if __name__ == "__main__":
    app.run(debug=True, )
