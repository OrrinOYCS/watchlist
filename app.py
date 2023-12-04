import os.path
import sys
import click
from flask import Flask, render_template, app, request, flash, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# 判断系统类型决定路径分割线
WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'

# 初始化flask以及sqlalchemy数据库
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'dev'
db = SQLAlchemy(app)

# 用户验证界面,要放到一开始
login_manager = LoginManager(app)
# 在login_required保护之后自动跳转的视图定义
login_manager.login_view = 'login'


# 将之定义为装饰器用来返回加载的用户
@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))
    return user


# 定义两张表
# 为User继承一个UserMixin使之能够被flask判断登陆状态
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    username = db.Column(db.String(20))
    password_hash = db.Column(db.String(128))

    # 用werkzeug哈希管理密码
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)


# 登陆页面
# 这里的GET是用来渲染视图的，POST是用来提交表单的
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not username or not password:
            flash('invalid input')
            return redirect(url_for('login'))
        user = User.query.first()
        if username == user.username and user.validate_password(password):
            # 登陆用户
            login_user(user)
            flash('login success')
            return redirect(url_for('index'))
        else:
            print(user.validate_password(password))
            print(user.username)
            print(username)
            flash('login fail')
            return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('byebye')
    return redirect(url_for('index'))


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    year = db.Column(db.String(4))


# 模板渲染数据库中的数据，index写好的html
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if not current_user.is_authenticated:
            return redirect(url_for('index'))
        title = request.form.get('title')
        year = request.form.get('year')
        if not title or not title or len(year) > 4 or len(title) > 60:
            flash("Invalid input!")
            return redirect(url_for("index"))
        movie = Movie(title=title, year=year)
        db.session.add(movie)
        db.session.commit()
        flash("Insert success!")
        return redirect(url_for("index"))
    movie = Movie.query.all()
    return render_template('index.html', movie=movie)


@app.route('/settings', methods =['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        if not current_user.is_authenticated:
            return redirect(url_for('index'))
        username = request.form['username']
        if not username or len(username)>20:
            flash('invalid input')
            return redirect(url_for('settings'))
        current_user.username = username
        db.session.commit()
        flash('setting success')
        return redirect(url_for('index'))
    return render_template('settings.html')
@app.route('/movie/edit/<int:movie_id>', methods=['GET', 'POST'])
@login_required
def edit(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    if request.method == 'POST':
        title = request.form['title']
        year = request.form['year']
        if not title or not year or len(year) > 4 or len(title) > 60:
            flash("Invalid input!")
            return redirect(url_for('edit', movie_id=movie_id))
        movie.title = title
        movie.year = year
        db.session.commit()
        flash("Edit success!")
        return redirect(url_for('index'))
    return render_template('edit.html', movie=movie)


@app.route('/movie/delete/<int:movie_id>', methods=['POST'])
@login_required
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash("Delete success!")
    return redirect(url_for('index'))


@app.cli.command()
def forge():
    db.drop_all()
    db.create_all()
    name = "Orrin"
    movies = [
        {'title': 'jingqiduizhang', 'year': '2023'},
        {'title': 'shentounaiba', 'year': '2022'},
        {'title': 'yinhehuweidui3', 'year': '2023'},
        {'title': 'xiaoshenkedejiushu', 'year': '1997'},
        {'title': 'aganzhengzhuan', 'year': '1997'},
        {'title': 'taitannikehao', 'year': '1997'}
    ]

    user = User(name=name)
    db.session.add(user)
    for m in movies:
        movie = Movie(title=m['title'], year=m['year'])
        db.session.add(movie)
    db.session.commit()
    click.echo('job done.')


@app.cli.command()
@click.option('--drop', is_flag=True, help='create after drop')
def initdb(drop):
    if drop:
        db.drop_all()
    db.create_all()
    click.echo('initialized database')


@app.cli.command()
@click.option('--username', prompt=True, help='The username used to login')
@click.option('--password', prompt=True, help='The password used to login', hide_input=True, confirmation_prompt=True)
def admin(username, password):
    db.create_all()
    user = User.query.first()
    if user is not None:
        click.echo('updating current user...')
        user.username = username
        user.set_password(password)
    else:
        click.echo('creating new user...')
        user = User(username=username, name='admin')
        user.set_password(password)
        db.session.add(user)
    db.session.commit()
    click.echo('job done')


@app.errorhandler(404)
def page_not_found(e):
    user = User.query.first()
    return render_template("404.html"), 404


# 加了装饰器，作为全局数据随意使用
@app.context_processor
def return_user():
    user = User.query.first()
    return dict(user=user)
