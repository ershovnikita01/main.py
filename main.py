from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_login import UserMixin


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqlite.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'thisisasecretkey'
db = SQLAlchemy(app)



class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    complete = db.Column(db.Boolean)
    userid = db.Column(db.Integer, db.ForeignKey('user.id'))
    tagid = db.Column(db.Integer, db.ForeignKey('tag.id'), nullable=True)



class User (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(128), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)

class Tag (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    userid = db.Column(db.Integer, db.ForeignKey('user.id'))


@app.route('/gettags')
def gettags():
    if 'userid' not in session:
        return redirect(url_for('reg'))
    else:
        tag_list = db.engine.execute('SELECT * FROM Todo WHERE userid=' + str(session['userid']))
        return render_template('base.html', tag_list = tag_list)


@app.route('/addtag', methods=['POST'])
def add_tag():
    title = request.form.get("title")
    new_tag = Tag(title=title, userid=session['userid'])
    db.session.add(new_tag)
    db.session.commit()
    return redirect(url_for("index"))


@app.route("/updatetag", methods=['POST'])
def updatetag():
    tag_id = request.form.get('id')
    name = request.form.get('title')
    tag = Tag.query.filter_by(id=tag_id).first()
    tag.title = name
    db.session.commit()
    return redirect(url_for("index"))



@app.route("/deletetag/<int:tag_id>")
def deletetag(tag_id):
    tag = Tag.query.filter_by(id=tag_id).first()
    db.session.delete(tag)
    db.session.commit()
    return redirect(url_for("index"))


@app.route('/')
def index():
    if 'userid' not in session:
        return redirect(url_for('reg'))
    else:
        todo_list = db.engine.execute('SELECT * FROM Todo WHERE userid=' + str(session['userid']))
        tag_list = db.engine.execute('SELECT * FROM Tag WHERE userid=' + str(session['userid']))
        return render_template('base.html', todo_list = todo_list, tag_list=tag_list)


@app.route('/add', methods=['POST'])
def add():
    title = request.form.get("title")
    new_todo = Todo(title=title, complete=False, userid=session['userid'])
    db.session.add(new_todo)
    db.session.commit()
    return redirect(url_for("index"))


@app.route("/update/<int:todo_id>")
def update(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    todo.complete = not todo.complete
    db.session.commit()
    return redirect(url_for("index"))


@app.route("/delete/<int:todo_id>")
def delete(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for("index"))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(login=username).first()
        if user is not None:
            session['userid'] = user.id
            return redirect(url_for("index"))
        else:
            return redirect(url_for('error', msg='Такого пользователя не существует!'))


@app.route('/reg', methods=['GET', 'POST'])
@app.route('/registration', methods=['GET', 'POST'])
def reg():
    if request.method == 'GET':
        return render_template('reg.html')
    else:
        username = request.form.get('username')
        password = request.form.get('password')
        print("user")
        if User.query.filter_by(login=username).first() is not None:
            return redirect(url_for('error', msg='Такой пользователь уже есть!'))
        else:
            new_user = User(login=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            session['userid'] = new_user.id
            return redirect(url_for("index"))


@app.route('/error/<string:msg>')
def error(msg):
    return render_template('error.html', msg=msg)


@app.route('/logout')
def logout():
    session.pop('userid', None)
    return render_template('logout.html')


@app.route('/add_to_todo/<int:todo_id>', methods=['POST'])
def add_to_todo(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    tag_name = request.form.get('title')
    tag = Tag.query.filter_by(title=tag_name).first()
    if tag is None:
        return redirect(url_for('error', msg='Такого тэга нет!'))
    todo.tagid = tag.title
    db.session.commit()
    return redirect(url_for("index"))




if __name__ == "__main__":
    db.create_all()
    db.create_all()
    app.run(debug=True)
