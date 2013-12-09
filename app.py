import os, json, base64, time, pymongo, json , gevent, uuid, sqlite3, logging
from flask import Flask, request, g, redirect, url_for, render_template, make_response
from flask.ext.assets import Environment
from core import TodoStack, Todo, StackCommandDispatcher
from Mappers import MapperFactory
from werkzeug.debug import DebuggedApplication
from gevent.pywsgi import WSGIServer
from webassets.script import CommandLineEnvironment

app = Flask(__name__)
assets = Environment(app)
factory = MapperFactory("sqlite")

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect("db");
    return db

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.executescript(f.read())
            db.commit()
init_db();
@app.route('/')
def createStack():
    url = "/" + base64.b64encode(str(time.time()))
    return redirect(url.strip(' \t\n\r%\\') )

@app.route('/<stackName>')
def displayStack(stackName):
    stack = factory.getMapper().findByName(stackName, get_db()) or TodoStack(None, stackName)
    trash_stack = factory.getMapper().findByName(stackName + "_trash", get_db()) or TodoStack(None, stackName + "_trash")
    response = make_response(render_template("display_stack.html", stack=stack, trash_stack=trash_stack))
    response.set_cookie("sequenceNumber", str(StackCommandDispatcher.openDispatcher(stackName).get_max_sequence_number()))
    return response

@app.route('/<stackName>/push/', methods=["POST"])
def pushItem(stackName):
    stack = factory.getMapper().findByName(stackName, get_db()) or TodoStack(None, stackName)
    stack.push(request.form['item'])
    factory.getMapper().store(stack, get_db())
    todo = stack.peek()
    command = {"command": "push", "data": {"id": str(todo.id), "content":todo.content, "priority": todo.priority, "stackid": str(todo.stackid), "order": todo.order}}
    StackCommandDispatcher.openDispatcher(stackName).new_command([command])
    return json.dumps({"response": "success", "commands": [command]})

@app.route('/<stackName>/pop/', methods=["GET"])
def popItem(stackName):
    stack = factory.getMapper().findByName(stackName, get_db()) or TodoStack(None, stackName)
    trash_stack = factory.getMapper().findByName(stackName + "_trash", get_db()) or TodoStack(None, stackName + "_trash")
    todo = stack.pop()
    trash_stack.push(todo)
    factory.getMapper().store(stack, get_db())
    factory.getMapper().store(trash_stack, get_db())
    command = {"command": "pop", "data": {"id": str(todo.id), "content":todo.content, "priority": todo.priority, "stackid": str(todo.stackid), "order": todo.order}}
    StackCommandDispatcher.openDispatcher(stackName).new_command([command])
    return json.dumps({"response": "success", "commands": [command]})

@app.route('/<stackName>/moveItem/<int:fromIndex>/<int:toIndex>/', methods=["GET"])
def moveItem(stackName, fromIndex, toIndex):
    stack = factory.getMapper().findByName(stackName, get_db()) or TodoStack(None, stackName)
    stack.moveItem(fromIndex, toIndex)
    factory.getMapper().store(stack, get_db())
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

@app.route('/<stackName>/removeItem/<int:index>/', methods=["GET"])
def removeItem(stackName, index):
    stack = factory.getMapper().findByName(stackName, get_db()) or TodoStack(None, stackName)
    todos = stack.getItems(True)
    todo = todos[index]
    stack.removeItem(index)
    factory.getMapper().store(stack, get_db())
    command = {"command": "removeItem", "data": {"id": str(todo.id), "content":todo.content, "priority": todo.priority, "stackid": str(todo.stackid), "order": todo.order}}
    StackCommandDispatcher.openDispatcher(stackName).new_command([command])
    return json.dumps({"response": "success", "commands": [command]})

@app.route('/<stackName>/raisePriority/<int:index>/', methods=["GET"])
def raisePriority(stackName, index):
    stack = factory.getMapper().findByName(stackName, get_db()) or TodoStack(None, stackName)
    todos = stack.getItems(True)
    todo = todos[index]
    todo.priority += 1
    if todo.priority >= 5:
        todo.priority %= 5
    factory.getMapper().store(stack, get_db())
    command = {"response": "success", "commands": [{"command": "update", "data": {"id": str(todo.id), "content":todo.content, "priority": todo.priority, "stackid": str(todo.stackid), "order": todo.order}}]}
    StackCommandDispatcher.openDispatcher(stackName).new_command([command])
    return json.dumps({"response": "success", "commands": [command]})

@app.route('/<stackName>/fetch/<int:request_sequence_number>/', methods=["GET"])
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
    # cmdenv.invoke('build')
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

app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
app.debug = True
