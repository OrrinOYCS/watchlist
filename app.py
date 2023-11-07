from flask import Flask, render_template

app = Flask(__name__)

name = "Orrin"
movies = [
    {'title': 'a', 'year': '1998'},
    {'title': 'king of comedy', 'year': '1999'},
    {'title': 'asfd dfasd ', 'year': '2003'},
    {'title': 'ef safwarqw ', 'year': '2008'},
    {'title': 'sdf dfwaf ', 'year': '2002'},
    {'title': 'yik u tjdj ', 'year': '2004'},
    {'title': 't ru  urs ', 'year': '2016'}
]


@app.route('/')
@app.route('/home')
def index():
    return render_template('index.html', name=name, movies=movies)
