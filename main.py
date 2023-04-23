import os

from flask import *
from flask_login import LoginManager, login_user, login_required, logout_user

from PIL import Image

import random

from data import db_session
from data.users import User
from data.news import News
from data.loginform import LoginForm
from data.regform import RegisterForm
from data import news_api
from data.news_form import NewsForm


def mem():
    f = random.choice(os.listdir("static/mem_days/"))
    return f'static/mem_days/{f}'


app = Flask('memcreator')
app.config['SECRET_KEY'] = 'memes_hehe'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(_):
    return make_response(jsonify({'error': 'Bad Request'}), 400)


@app.route('/')
def main():
    global days_mem
    params = {}
    params["title"] = "memcreator"
    return render_template('main.html', **params, days_mem=mem())


@app.route('/login', methods=['GET', 'POST'])
def login():
    global days_mem
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            session['id'] = user.id
            return redirect("/feed")
        return render_template('log.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('log.html', title='Авторизация', form=form, days_mem=mem())


@app.route('/<login>')
def user(login):
    global days_mem
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.login == login).first()
    if user == None:
        flash('User ' + login + ' not found.')
        return redirect('/login')
    news = db_sess.query(News).filter(News.user_id == session['id'])
    return render_template('user.html',
                           user=user, news=news, days_mem=mem())


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/feed')
def feed():
    global days_mem
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.is_private != True)
    return render_template("feed.html", news=news, days_mem=mem())


@app.route('/create', methods=['POST', 'GET'])
def create():
    global days_mem
    form = NewsForm()
    db_sess = db_session.create_session()
    if form.validate_on_submit():
        news = News(
            title=form.name.data,
            content=form.about.data,
            is_private=form.private.data,
            user_id=session['id']
        )
        db_sess.add(news)
        db_sess.commit()
        f = request.files['pic_mem']
        split_tup = os.path.splitext(f.filename)
        file_extension = split_tup[1]
        filename = f'{str(news.id)}{file_extension}'
        f.save(os.path.join('static/post_id', filename))
        img = Image.open(f'static/post_id/{filename}')
        img.thumbnail(size=(500, 500))
        os.remove(f'static/post_id/{filename}')
        img.save(f'static/post_id/{filename}')
        news.image = f'static/post_id/{filename}'
        img = Image.open(f'static/post_id/{filename}')
        img.thumbnail(size=(250, 250))
        img.save(f'static/mem_days/{filename}')
        db_sess.commit()
        return redirect('/feed')
    return render_template("create.html", form=form, days_mem=mem())


@app.route('/registr', methods=['GET', 'POST'])
def reqister():
    global days_mem
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('reg.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают", days_mem=days_mem)
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('reg.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть", days_mem=days_mem)
        if db_sess.query(User).filter(User.login == form.login.data).first():
            return render_template('reg.html', title='Регистрация',
                                   form=form,
                                   message="Такой логин занят", days_mem=mem())
        user = User(
            name=form.name.data,
            email=form.email.data,
            login=form.login.data,
            about=form.about.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        try:
            f = request.files['picture']
            split_tup = os.path.splitext(f.filename)
            file_extension = split_tup[1]
            filename = f'{str(user.id)}{file_extension}'
            f.save(os.path.join('static/user_pic', filename))
            user.avatar(user, db_sess, filename)
        except:
            user.picture = 'static/user_pic/unnamed.jpg'
        return redirect('/login')
    return render_template('reg.html', title='Регистрация', form=form, days_mem=mem())


if __name__ == '__main__':
    db_session.global_init("db/blogs.db")
    app.register_blueprint(news_api.blueprint)
    app.run(port=8080, host='127.0.0.1')
