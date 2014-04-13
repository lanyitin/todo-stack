import hashlib, json, os 
from flask import Flask, request, g, redirect, url_for, render_template, make_response, Response
from flask.ext.assets import Environment
from flask.ext.login import LoginManager, login_user , logout_user , current_user , login_required
from flask.ext.sqlalchemy import SQLAlchemy
from core.model import db, Todo, User, Tag
from facade import Facade
from sqlalchemy import and_, desc

login_manager = LoginManager()
facade = Facade()
app = Flask(__name__)
db.init_app(app)
assets = Environment(app)
login_manager.init_app(app)
login_manager.login_view = "login"

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://{0}:{1}@{2}:{3}/stacktodos?collation=utf8_general_ci&use_unicode=true&charset=utf8'.format(os.environ['STACKTODOS_MYSQL_DB_USERNAME'], os.environ['STACKTODOS_MYSQL_DB_PASSWORD'], os.environ['STACKTODOS_MYSQL_DB_HOST'], os.environ['STACKTODOS_MYSQL_DB_PORT'])
app.secret_key = 'e6cb00fb23790ba6d43de3826639aae2'


def todo2dict(todo):
    tags = list()
    for tag in todo.tags:
        tags.append(tag.name)
    return {"id": todo.id, "content":todo.content, "priority": todo.priority, "order": todo.order, "tags": tags}

def todo2json(todo):
    return json.dumps(todo2dict(todo))


app.jinja_env.filters['todo2json'] = todo2json


@app.before_request
def before_request():
    g.user = current_user


@login_manager.user_loader
def load_user(id):
    return db.session.query(User).filter_by(id=id).first()


@app.errorhandler(500)
def page_not_found(error):
    return str(error)


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/login/', methods = ['GET', 'POST'])
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


@app.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main')) 


@app.route('/register/', methods = ['GET', 'POST'])
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


@app.route('/')
@login_required
def main():
    stack, trash_stack = facade.find_all_todos(g.user.id)
    return make_response(render_template("display_stack.html", stack=stack, trash_stack=trash_stack))


@app.route('/push/', methods=["POST"])
@login_required
def pushItem():
    todo = facade.push_todo(g.user.id, request.json["item"])
    return Response(json.dumps([todo2dict(todo)]), mimetype='application/json')


@app.route('/append/', methods=["POST"])
@login_required
def appendItem():
    response = facade.append_todo(g.user.id, request.json["item"])
    response = map(todo2dict, response);
    return Response(json.dumps(response), mimetype='application/json')


@app.route('/moveToTrash/<int:todoid>/', methods=["GET"])
@login_required
def moveToTrash(todoid):
    todo = facade.move_todo_to_trash(todoid);
    if todo is not None:
        return Response(json.dumps([todo2dict(todo)]), mimetype='application/json')


@app.route('/moveItem/<int:fromIndex>/<int:toIndex>/', methods=["GET"])
@login_required
def moveItem(fromIndex, toIndex):
    response = facade.move_todo(g.user.id, fromIndex, toIndex);
    response = map(todo2dict, response);
    return Response(json.dumps(response), mimetype='application/json')


@app.route('/removeItem/<int:todoid>/', methods=["GET"])
@login_required
def removeItem(todoid):
    todo = facade.move_todo_to_trash(todoid);
    return Response(json.dumps([todo2dict(todo)]), mimetype='application/json')


@app.route('/clean_trash/', methods=["GET"])
@login_required
def cleanTrash():
    response = facade.clean_trash(g.user.id);
    response = map(todo2dict, response);
    return Response(json.dumps(response), mimetype='application/json')


@app.route('/raisePriority/<int:todoid>/', methods=["GET"])
@login_required
def raisePriority(todoid):
    todo = facade.raise_priority(todoid)
    return Response(json.dumps([todo2dict(todo)]), mimetype='application/json')


@app.route('/tag/list/', methods=["GET"])
@login_required
def tagList():
    return make_response(str(facade.find_all_tag(g.user.id)))


@app.route('/tag/<tagName>/')
@login_required
def displayTag(tagName):
    stack, trash_stack = facade.find_by_tag(g.user.id, tagName)
    return make_response(render_template("display_stack.html", stack=stack, trash_stack=trash_stack))
