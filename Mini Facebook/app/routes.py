from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, StatusUpdate, MessageForm
from app.models import User, Post , Message
from datetime import datetime

@app.route('/')
@app.route('/index')
@app.route('/',methods=['GET', 'POST'])
@app.route('/index',methods=['GET', 'POST'])
@login_required
def index():
    form = StatusUpdate()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Status is updated')
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(page, app.config['POST_PER_PAGE'], False)
    if posts.next_num :
        next_url = url_for('index', page=posts.next_num)
    else :
        next_url = None
    if posts.prev_num :
        prev_url = url_for('index', page=posts.prev_num)
    else :
        prev_url = None
    return render_template('index.html', title='Timeline', posts=posts.items, form=form, next_url=next_url, prev_url=prev_url)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index',user = user)
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form= form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(user_id=current_user.id).order_by(
            Post.timestamp.desc()).paginate(page,app.config['POST_PER_PAGE'],False)
    if posts.next_num:
        next_url = url_for('user',username = current_user.username, page=posts.next_num)
    else :
        next_url = None
    if posts.prev_num :
        prev_url = url_for('user',username = current_user.username, page=posts.prev_num)
    else :
        prev_url = None
    return render_template('user.html', user=user, posts=posts.items, next_url=next_url, prev_url=prev_url)

@app.route('/edit_profile',methods = ['GET','POST'])
@login_required
def edit_profile():
     form = EditProfileForm()
     if form.validate_on_submit() or request.method == 'POST':
         current_user.about_me = form.about_me.data
         current_user.relationship_status = form.relationship_status.data
         current_user.gender = form.gender.data
         current_user.country = form.country.data
         db.session.commit()
         return redirect(url_for('user',username= current_user.username))
     return render_template('edit_profile.html',title = 'Editing Profile',form = form)

@app.before_request
def before_request():
    if current_user.is_authenticated :
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/follow/<username>',methods = ['POST','GET'])
@login_required
def follow(username):
    user = User.query.filter_by(username= username).first()
    if user is None:
        flash('User does not exist')
        return redirect(url_for('user', username=username))
    if user.username == current_user.username :
        flash('You can not follow yourself')
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {0}'.format(user.username))
    return redirect(url_for('user', username=username))

@app.route('/unfollow/<username>',methods = ['POST','GET'])
@login_required
def unfollow(username):
    user= User.query.filter_by(username=username).first()
    if user is None:
        flash('User does not exist')
        return redirect(url_for('user', username=username))
    if user.username == current_user.username :
        flash('You can not unfollow yourself')
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are unfollowing {0}'.format(user.username))
    return redirect(url_for('user', username=username))

@app.route('/send_message/<receiver>',methods = ['POST','GET'])
@login_required
def send_message(receiver):
    user = User.query.filter_by(username = receiver).first_or_404()
    form = MessageForm()
    if form.validate_on_submit():
        message = Message(text= form.message.data,reader=user, author =current_user)
        db.session.add(message)
        db.session.commit()
        flash('Your Message is delivered')
        return redirect(url_for('user', username=current_user.username))
    return render_template('send_message.html',receiver=receiver, form=form)

@app.route('/messages')
@login_required
def messages():
    current_user.last_message_read_time = datetime.utcnow()
    db.session.commit()
    page = request.args.get('page', 1, type=int)
    messages = current_user.message_received.order_by(
        Message.timestamp.desc()).paginate(
            page, app.config['MESSAGE_PER_PAGE'], False)

    next_url = url_for('messages', page=messages.next_num) \
        if messages.has_next else None
    prev_url = url_for('messages', page=messages.prev_num) \
        if messages.has_prev else None
    return render_template('messages.html', messages=messages.items,
                           next_url=next_url, prev_url=prev_url)