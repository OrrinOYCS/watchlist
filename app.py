import os.path
import sys
import click
from flask import Flask, render_template, app, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

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


# 定义两张表
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    year = db.Column(db.String(4))


# 模板渲染数据库中的数据，index写好的html
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
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


@app.route('/movie/edit/<int:movie_id>', methods=['GET', 'POST'])
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


@app.errorhandler(404)
def page_not_found(e):
    user = User.query.first()
    return render_template("404.html"), 404


# 加了装饰器，作为全局数据随意使用
@app.context_processor
def return_user():
    user = User.query.first()
    return dict(user=user)
