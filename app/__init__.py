import base64, hashlib, json, logging, os, re, sqlite3, sys, time, uuid
from datetime import datetime
from flask import Flask, request, g, redirect, url_for, render_template, make_response, Response
from flask.ext.assets import Environment
from flask.ext.login import LoginManager, login_user , logout_user , current_user , login_required
from flask.ext.sqlalchemy import SQLAlchemy
from core.model import db, Todo, User, Tag
from sqlalchemy import and_, desc

login_manager = LoginManager()
app = Flask(__name__)
db.init_app(app)
assets = Environment(app)
login_manager.init_app(app)
login_manager.login_view = "/login"

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://{0}:{1}@{2}:{3}/stacktodos?collation=utf8_general_ci&use_unicode=true&charset=utf8'.format(os.environ['STACKTODOS_MYSQL_DB_USERNAME'], os.environ['STACKTODOS_MYSQL_DB_PASSWORD'], os.environ['STACKTODOS_MYSQL_DB_HOST'], os.environ['STACKTODOS_MYSQL_DB_PORT'])
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
app.debug = True

def todo2json(todo):
    return json.dumps(todo2dict(todo))

app.jinja_env.filters['todo2json'] = todo2json


@app.before_request
def before_request():
    g.user = current_user

@login_manager.user_loader
def load_user(id):
    return db.session.query(User).filter_by(id=id).first()


@app.route('/login', methods = ['GET', 'POST'])
def login():
    if g.user is not None and g.user.is_authenticated():
	    return redirect(request.args.get("next") or url_for("main"))

    if request.method == 'GET':
        return render_template('login.html')

    username = request.form['username']
    password = hashlib.md5(request.form['password']).hexdigest()
    registered_user = User.query.filter_by(username = username, password = password).first()
    if registered_user is None:
        return redirect(url_for('login'))
    login_user(registered_user)
    return redirect(request.args.get("next") or url_for("main"))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main')) 

@app.route('/')
@login_required
def main():
    stack = Todo.query.filter_by(owner_user_id = g.user.id, in_trash = False).order_by(desc(Todo.order)).all()
    trash_stack = Todo.query.filter_by(owner_user_id = g.user.id, in_trash = True).order_by(Todo.push_date_time).all()
    response = make_response(render_template("display_stack.html", stack=stack, trash_stack=trash_stack))
    return response

@app.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    username = request.form['username']
    email = request.form['email']
    password = hashlib.md5(request.form['password']).hexdigest()
    user = User(username = username, password = password, email = email)
    db.session.add(user);
    db.session.commit();
    return redirect(url_for('login'))

@app.route('/tag/<tagName>')
@login_required
def displayTag(tagName):
    stack = Todo.query.filter_by(owner_user_id = g.user.id, in_trash = False) \
        .filter(Todo.tags.any(name = tagName)).all()
    todo_stack = Todo.query.filter_by(owner_user_id = g.user.id, in_trash = True).all()
    trash_stack = Todo.query.filter_by(owner_user_id = g.user.id, in_trash = True).order_by(Todo.push_date_time).all()
    return make_response(render_template("display_stack.html", stack=stack, trash_stack=trash_stack))

@app.route('/push/', methods=["POST"])
@login_required
def pushItem():
    top_item = Todo.query.filter_by(owner_user_id=g.user.id, in_trash=False).order_by(desc(Todo.order)).first()
    todo = Todo(request.json['item'], g.user.id)
    if top_item is not None:
        todo.order = top_item.order + 1
    else:
        todo.order = 0
    db.session.add(todo)
    db.session.commit()
    return Response(json.dumps([todo2dict(todo)]), mimetype='application/json')

@app.route('/append/', methods=["POST"])
@login_required
def appendItem():
    todo = Todo(request.json['item'], g.user.id)

    stack = Todo.query.filter_by(owner_user_id=g.user.id, in_trash=False).order_by(Todo.order).all()
    if len(stack) > 0 and stack[0].order > 1:
        todo.order = stack[0].order - 1
    else:
        todo.order = 0
    response = []
    processed_item = todo
    db.session.add(todo)
    db.session.commit()
    response.append(todo2dict(todo))

    for top_item in stack:
        top_item.order = processed_item.order + 1
        db.session.add(top_item)
        response.append(todo2dict(top_item))
        processed_item = top_item

    db.session.commit()

    return Response(json.dumps(response), mimetype='application/json')

@app.route('/moveToTrash/<int:todoid>', methods=["GET"])
@login_required
def moveToTrash(todoid):
    top_item = Todo.query.filter_by(id=todoid).order_by(desc(Todo.order)).first()
    if top_item is not None:
        top_item.in_trash = True
        top_item.push_date_time = datetime.utcnow()
        db.session.add(top_item)
        db.session.commit()
        todo = top_item
        command = {"command": "pop", "data": todo2dict(todo)}
        return json.dumps({"response": "success", "commands": [command]})

@app.route('/moveItem/<int:fromIndex>/<int:toIndex>/', methods=["GET"])
@login_required
def moveItem(fromIndex, toIndex):
    stack = Todo.query.filter_by(owner_user_id = g.user.id, in_trash = False).order_by(desc(Todo.order)).all()
    response = {"response": "success", "commands": []}
    begin = end = 0
    if (fromIndex > toIndex):
        begin = toIndex
        end = fromIndex
	fromIndex -= toIndex
	toIndex -= toIndex
    else:
        end = toIndex
        begin = fromIndex
	toIndex -= fromIndex
	fromIndex -= fromIndex

    item_slice = stack[begin:end + 1]
    order_slice = [item.order for item in item_slice]
    item_slice.insert(toIndex, item_slice.pop(fromIndex))

    for order, todo in zip(order_slice, item_slice):
        todo.order = order
        db.session.add(item)
        command = {"command":"update", "data":todo2dict(todo)}
        response["commands"].append(command)

    db.session.commit()
    return json.dumps(response)

@app.route('/removeItem/<int:todoid>/', methods=["GET"])
@login_required
def removeItem(todoid):
    todo = Todo.query.filter_by(id = todoid).first()
    db.session.delete(todo)
    db.session.commit()
    tags = Tag.query.filter_by(owner_user_id=g.user.id).all()
    tags = [tag for tag in tags if len(tag.todos) is 0]
    for tag in tags:
        db.session.delete(tag)
    db.session.commit()
    return Response(json.dumps([todo2dict(todo)]), mimetype='application/json')

@app.route('/tag/list', methods=["GET"])
@login_required
def tagList():
    return make_response( str(Tag.query.filter_by(owner_user_id = g.user.id).all()) )
@app.route('/clean_trash', methods=["GET"])
@login_required
def cleanTrash():
    todos = Todo.query.filter_by(owner_user_id = g.user.id, in_trash = True).all()
    commands = []
    for todo in todos:
        db.session.delete(todo)
        command = {"command": "removeItem", "data": todo2dict(todo)}
        commands.append(command)
    db.session.commit()
    tags = Tag.query.filter_by(owner_user_id=g.user.id).all()
    tags = [tag for tag in tags if len(tag.todos) is 0]
    for tag in tags:
        db.session.delete(tag)
    db.session.commit()
    return json.dumps({"response": "success", "commands": commands})

@app.route('/raisePriority/<int:todoid>/', methods=["GET"])
@login_required
def raisePriority(todoid):
    todo = Todo.query.filter_by(id = todoid).first()
    todo.priority += 1
    if todo.priority >= 5:
        todo.priority %= 5
    db.session.add(todo)
    db.session.commit()
    command = {"response": "success", "commands": [{"command": "update", "data": todo2dict(todo)}]}
    return Response(json.dumps([todo2dict(todo)]), mimetype='application/json')

@app.errorhandler(500)
def page_not_found(error):
    return str(error)

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def todo2dict(todo):
    tags = list()
    for tag in todo.tags:
        tags.append(tag.name)
    return {"id": todo.id, "content":todo.content, "priority": todo.priority, "order": todo.order, "tags": tags}
