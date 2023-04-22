import os

from flask import *
from flask_login import LoginManager, login_user, login_required, logout_user
from flask import make_response

from data import db_session
from data.users import User
from data.news import News
from data.loginform import LoginForm
from data.regform import RegisterForm
from data import news_api

app = Flask(__name__)
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
    params = {}
    params["title"] = "memcreator"
    return render_template('main.html', **params)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/feed")
        return render_template('log.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('log.html', title='Авторизация', form=form)


@app.route('/<login>')
def user(login):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.login == login).first()
    if user == None:
        flash('User ' + login + ' not found.')
        return redirect('/login')
    news = db_sess.query(News).filter(News.user_id == 3)
    return render_template('user.html',
                           user=user, news=news)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/feed')
def feed():
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.is_private != True)
    return render_template("feed.html", news=news)


@app.route('/registr', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('reg.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('reg.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        if db_sess.query(User).filter(User.login == form.login.data).first():
            return render_template('reg.html', title='Регистрация',
                                   form=form,
                                   message="Такой логин занят")
        user = User(
            name=form.name.data,
            email=form.email.data,
            login=form.login.data,
            about=form.about.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        f = request.files['file']
        split_tup = os.path.splitext(f.filename)
        file_extension = split_tup[1]
        filename = f'{str(user.id)}{file_extension}'
        f.save(os.path.join('static/user_pic', filename))
        user.avatar(user, db_sess, filename)
        return redirect('/login')
    return render_template('reg.html', title='Регистрация', form=form)


if __name__ == '__main__':
    db_session.global_init("db/blogs.db")
    app.register_blueprint(news_api.blueprint)
    app.run(port=8080, host='127.0.0.1')
