# app/routes.py
from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, EmptyForm, PostForm, SnackForm, RatingForm, SearchForm
from app.models import User, Snack, Rating
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.urls import url_parse
from datetime import datetime

@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    snacks = Snack.query.order_by(Snack.timestamp.desc()).paginate(
        page=page, per_page=app.config['SNACKS_PER_PAGE'], error_out=False)
    next_url = url_for('index', page=snacks.next_num) if snacks.has_next else None
    prev_url = url_for('index', page=snacks.prev_num) if snacks.has_prev else None
    return render_template('index.html', title='Home', snacks=snacks.items, next_url=next_url, prev_url=prev_url)

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
            next_page = url_for('index')
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
    return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    # Für 'Follow' / 'Unfollow'
    form = EmptyForm()
    return render_template('user.html', user=user, posts=posts, form=form)

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)

@app.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User {} not found.'.format(username))
            return redirect(url_for('index'))
        if user == current_user:
            flash('You cannot follow yourself you self loving fucker!')
            return redirect(url_for('user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash('You are following {}!'.format(username))
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))
    
@app.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User {} not found.'.format(username))
            return redirect(url_for('index'))
        if user == current_user():
            flash('You cannot unfollow yourself, remember you are your best friend!')
            return redirect(url_for('user', username=username))
        else:
            return redirect(url_for('index'))

@app.route('/explore', methods=['GET', 'POST'])
@login_required
def explore():
    search_form = SearchForm()
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('q', '')

    if search_query:
        snacks = Snack.query.filter(Snack.name.like(f'%{search_query}%') | Snack.category.like(f'%{search_query}%')).paginate(
            page=page, per_page=app.config['SNACKS_PER_PAGE'], error_out=False)
    else:
        snacks = Snack.query.order_by(Snack.timestamp.desc()).paginate(
            page=page, per_page=app.config['SNACKS_PER_PAGE'], error_out=False)

    next_url = url_for('explore', page=snacks.next_num, q=search_query) if snacks.has_next else None
    prev_url = url_for('explore', page=snacks.prev_num, q=search_query) if snacks.has_prev else None

    return render_template('explore.html', title='Explore', snacks=snacks.items, next_url=next_url, prev_url=prev_url, search_query=search_query)


@app.route('/add_snack', methods=['GET', 'POST'])
@login_required
def add_snack():
    form = SnackForm()
    if form.validate_on_submit():
        snack = Snack(name=form.name.data, description=form.description.data, category=form.category.data, user_id=current_user.id)
        db.session.add(snack)
        db.session.commit()
        flash('Snack successfully added!')
        return redirect(url_for('index'))
    return render_template('add_snack.html', title='Add Snack', form=form)

@app.route('/snack/<int:snack_id>', methods=['GET', 'POST'])
@login_required
def snack(snack_id):
    snack = Snack.query.get_or_404(snack_id)
    form = RatingForm()
    if form.validate_on_submit():
        rating = Rating(rating=form.rating.data, comment=form.comment.data, user_id=current_user.id, snack_id=snack.id)
        db.session.add(rating)
        db.session.commit()
        flash('Your rating has been added!')
        return redirect(url_for('snack', snack_id=snack_id))
    ratings = Rating.query.filter_by(snack_id=snack.id).all()
    return render_template('snack.html', snack=snack, form=form, ratings=ratings)
