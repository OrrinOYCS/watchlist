import os.path
import sys
import click
from flask import Flask, render_template, app
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
@app.route('/')
@app.route('/home')
def index():
    user = User.query.first()
    movie = Movie.query.all()
    return render_template('index.html', user=user, movie=movie)


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
