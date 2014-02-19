import os, json, base64, time, pymongo, json , gevent, uuid, sqlite3, logging, hashlib
from flask import Flask, request, g, redirect, url_for, render_template, make_response
from flask.ext.assets import Environment
from flask.ext.login import LoginManager, login_user , logout_user , current_user , login_required
from core import TodoStack, Todo, StackCommandDispatcher, MapperFactory, User, UserMapper
from webassets.script import CommandLineEnvironment

login_manager = LoginManager()
app = Flask(__name__)
app.debug = True
assets = Environment(app)
login_manager.init_app(app)
login_manager.login_view = "/login"


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        mongo_con = pymongo.Connection(os.environ['OPENSHIFT_MONGODB_DB_HOST'], int(os.environ['OPENSHIFT_MONGODB_DB_PORT']))

        mongo_db = mongo_con[os.environ['OPENSHIFT_APP_NAME']]
        mongo_db.authenticate(os.environ['OPENSHIFT_MONGODB_DB_USERNAME'], os.environ['OPENSHIFT_MONGODB_DB_PASSWORD'])
        db = mongo_db
    return db

def get_mapper():
    mapper = g.get('mapper', None)
    if mapper is None:
        mapper = g.mapper = MapperFactory("mongo").getMapper()
    return mapper 

@app.before_request
def before_request():
    g.user = current_user

@login_manager.user_loader
def load_user(id):
    return UserMapper.findById(id,  get_db())


@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    username = request.form['username']
    password = hashlib.md5(request.form['password']).hexdigest()
    registered_user = UserMapper.findByUsernameAndPassword(username, password, get_db())
    if registered_user is None:
        return redirect(url_for('login'))
    login_user(registered_user)
    return redirect(url_for('main'))

@app.route('/')
@login_required
def main():
    return render_template('layout.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main')) 

@app.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    username = request.form['username']
    password = hashlib.md5(request.form['password']).hexdigest()
    user = User(username = username, password = password, authenticated = False, id = None)
    UserMapper.register(user, get_db())
    return redirect(url_for('login'))

@app.route('/stack/<stackName>')
@login_required
def displayStack(stackName):
    try:
        stack = get_mapper().findByNameAndUserId(stackName, g.user.id, get_db()) or TodoStack(None, stackName)
    except Exception:
        stack = TodoStack(None, stackName)
    try:
        trash_stack = get_mapper().findByNameAndUserId("trash", g.user.id, get_db()) or TodoStack(None, "trash")
    except Exception:
        trash_stack = TodoStack(None, stackName + "_trash")
    response = make_response(render_template("display_stack.html", stack=stack, trash_stack=trash_stack))
    response.set_cookie("sequenceNumber", str(StackCommandDispatcher.openDispatcher(stackName).get_max_sequence_number()))
    return response

@app.route('/stack/<stackName>/push/', methods=["POST"])
@login_required
def pushItem(stackName):
    try:
        stack = get_mapper().findByNameAndUserId(stackName, g.user.id, get_db()) or TodoStack(None, stackName)
    except Exception:
        stack = TodoStack(None, stackName)
    try:
        trash_stack = get_mapper().findByNameAndUserId("trash", g.user.id, get_db()) or TodoStack(None, "trash")
    except Exception:
        trash_stack = TodoStack(None, stackName + "_trash")
    stack.push(Todo(content = request.form['item']))
    get_mapper().store(stack, get_db())
    todo = stack.peek()
    command = {"command": "push", "data": {"id": str(todo.id), "content":todo.content, "priority": todo.priority, "stackid": str(todo.stackid), "order": todo.order}}
    StackCommandDispatcher.openDispatcher(stackName).new_command([command])
    return json.dumps({"response": "success", "commands": [command]})

@app.route('/stack/<stackName>/pop/', methods=["GET"])
@login_required
def popItem(stackName):
    try:
        stack = get_mapper().findByNameAndUserId(stackName, g.user.id, get_db()) or TodoStack(None, stackName)
    except Exception:
        stack = TodoStack(None, stackName)
    try:
        trash_stack = get_mapper().findByNameAndUserId("trash", g.user.id, get_db()) or TodoStack(None, "trash")
    except Exception:
        trash_stack = TodoStack(None, stackName + "_trash")
    todo = stack.pop()
    trash_stack.push(todo)
    get_mapper().store(stack, get_db())
    get_mapper().store(trash_stack, get_db())
    command = {"command": "pop", "data": {"id": str(todo.id), "content":todo.content, "priority": todo.priority, "stackid": str(todo.stackid), "order": todo.order}}
    StackCommandDispatcher.openDispatcher(stackName).new_command([command])
    return json.dumps({"response": "success", "commands": [command]})

@app.route('/stack/<stackName>/moveItem/<int:fromIndex>/<int:toIndex>/', methods=["GET"])
@login_required
def moveItem(stackName, fromIndex, toIndex):
    try:
        stack = get_mapper().findByNameAndUserId(stackName, g.user.id, get_db()) or TodoStack(None, stackName)
    except Exception:
        stack = TodoStack(None, stackName)
    try:
        trash_stack = get_mapper().findByName(stackName + "_trash", get_db())
    except Exception:
        trash_stack = TodoStack(None, stackName + "_trash")
    fromIndex = abs(fromIndex - stack.size() + 1)
    toIndex = abs(toIndex - stack.size() + 1)
    stack.moveItem(fromIndex, toIndex)
    get_mapper().store(stack, get_db())
    todos = stack.getItems(True)
    response = {"response": "success", "commands": []}
    begin = end = 0
    if (fromIndex > toIndex):
        begin = toIndex
        end = fromIndex
    else:
        end = toIndex
        begin = fromIndex
    for i in range(begin, end + 1):
        todo = todos[i]
        command = {"command":"update", "data":{"id": str(todo.id), "content":todo.content, "priority": todo.priority, "stackid": str(todo.stackid), "order": todo.order}}
        response["commands"].append(command)
    StackCommandDispatcher.openDispatcher(stackName).new_command(response["commands"])
    return json.dumps(response)

@app.route('/stack/<stackName>/removeItem/<int:index>/', methods=["GET"])
@login_required
def removeItem(stackName, index):
    try:
        stack = get_mapper().findByNameAndUserId(stackName, g.user.id, get_db()) or TodoStack(None, stackName)
    except Exception:
        stack = TodoStack(None, stackName)
    try:
        trash_stack = get_mapper().findByNameAndUserId("trash", g.user.id, get_db()) or TodoStack(None, stackName)
    except Exception:
        trash_stack = TodoStack(None, stackName + "_trash")
    index = abs(index - stack.size() + 1)
    print(index)
    todos = stack.getItems(False)
    todo = todos[index]
    stack.removeItem(index)
    get_mapper().store(stack, get_db())
    command = {"command": "removeItem", "data": {"id": str(todo.id), "content":todo.content, "priority": todo.priority, "stackid": str(todo.stackid), "order": todo.order}}
    StackCommandDispatcher.openDispatcher(stackName).new_command([command])
    return json.dumps({"response": "success", "commands": [command]})

@app.route('/stack/<stackName>/raisePriority/<int:index>/', methods=["GET"])
@login_required
def raisePriority(stackName, index):
    try:
        stack = get_mapper().findByNameAndUserId(stackName, g.user.id, get_db()) or TodoStack(None, stackName)
    except Exception:
        stack = TodoStack(None, stackName)
    try:
        trash_stack = get_mapper().findByNameAndUserId("trash", g.user.id, get_db()) or TodoStack(None, stackName)
    except Exception:
        trash_stack = TodoStack(None, stackName + "_trash")
    index = abs(index - stack.size() + 1)
    todos = stack.getItems(False)
    todo = todos[index]
    todo.priority += 1
    if todo.priority >= 5:
        todo.priority %= 5
    get_mapper().store(stack, get_db())
    command = {"response": "success", "commands": [{"command": "update", "data": {"id": str(todo.id), "content":todo.content, "priority": todo.priority, "stackid": str(todo.stackid), "order": todo.order}}]}
    StackCommandDispatcher.openDispatcher(stackName).new_command([command])
    return json.dumps({"response": "success", "commands": [command]})

@app.route('/stack/<stackName>/fetch/<int:request_sequence_number>/', methods=["GET"])
@login_required
def fetch(stackName, request_sequence_number):
    commands = StackCommandDispatcher.openDispatcher(stackName).fetch_command(request_sequence_number)
    response = make_response(json.dumps(commands))
    return response

@app.route('/rebuild_assets/', methods=["GET"])
def rebuild_assets():
    log = logging.getLogger('webassets')
    log.addHandler(logging.StreamHandler())
    log.setLevel(logging.DEBUG)

    cmdenv = CommandLineEnvironment(assets, log)
    cmdenv.build()
    return "success"

@app.errorhandler(500)
def page_not_found(error):
    return str(error)

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


if __name__ == "__main__":
    app.run()
