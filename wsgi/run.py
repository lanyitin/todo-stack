import os, sys, json, sqlite3, base64, time, pymongo, json , gevent, uuid, json, logging
from werkzeug.contrib.profiler import ProfilerMiddleware, MergeStream
from flask import Flask, request, g, abort, redirect, url_for, render_template, make_response
from flask.ext.assets import Environment, Bundle
from core import TodoStack, Todo
from Mappers import MapperFactory
from gevent import queue
from werkzeug.debug import DebuggedApplication
from gevent.pywsgi import WSGIServer


class StackCommandDispatcher:
    dispatchers = dict()
    @classmethod
    def openDispatcher(clazz, name):
        if not clazz.dispatchers.has_key(name):
            clazz.dispatchers[name] = StackCommandDispatcher(name)
        return clazz.dispatchers[name]

    def __init__(self, stackid):
        self.logger = logging.getLogger(__name__)
        self.stackid = stackid;
        self.cache = dict();
        self.evt = gevent.event.Event();
        self.latestCommand = None;

    def new_command(self, sequenceNumber, data):
        if self.latestCommand is not None:
            self.cache[self.latestCommand["key"]] = self.latestCommand
            self.logger.debug("cache" + str(self.cache))

        self.latestCommand = {"key": sequenceNumber, "commands": data}
        self.logger.debug("update latest command")
        self.evt.set()
        self.evt.clear()

    def fetch_command(self, sequenceNumber):
        commands = list()
        for key in self.cache:
            if key > sequenceNumber:
                self.logger.debug("append" + str(self.cache[key]))
                commands.append(self.cache[key])
        if len(commands) > 0:
            return commands
        if (self.latestCommand is not None and self.latestCommand["key"] >= sequenceNumber):
            commands.append(self.latestCommand)

        return commands

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        mongo_con = pymongo.Connection(os.environ['OPENSHIFT_MONGODB_DB_HOST'], int(os.environ['OPENSHIFT_MONGODB_DB_PORT']))

        mongo_db = mongo_con[os.environ['OPENSHIFT_APP_NAME']]
        mongo_db.authenticate(os.environ['OPENSHIFT_MONGODB_DB_USERNAME'], os.environ['OPENSHIFT_MONGODB_DB_PASSWORD'])
        db = mongo_db
    return db

app = Flask(__name__)
assets = Environment(app)
factory = MapperFactory("mongo")

@app.route('/')
def createStack():
    url = "/" + base64.b64encode(str(time.time()));
    return redirect(url.strip(' \t\n\r%\\') );

@app.route('/<stackName>')
def displayStack(stackName):
    stack = factory.getMapper().findByName(stackName, get_db()) or TodoStack(None, stackName);
    trash_stack = factory.getMapper().findByName(stackName + "_trash", get_db()) or TodoStack(None, stackName + "_trash");
    response = make_response(render_template("display_stack.html", stack=stack, trash_stack=trash_stack));
    response.set_cookie("sequenceNumber", str(0));
    return response;

@app.route('/<stackName>/push/<sequenceNumber>/', methods=["POST"])
def pushItem(stackName, sequenceNumber):
    stack = factory.getMapper().findByName(stackName, get_db()) or TodoStack(None, stackName);
    stack.push(request.form['item'])
    factory.getMapper().store(stack, get_db())
    todo = stack.peek()
    command = {"command": "push", "data": {"id": str(todo.id), "content":todo.content, "priority": todo.priority, "stackid": str(todo.stackid), "order": todo.order}};
    StackCommandDispatcher.openDispatcher(stackName).new_command(sequenceNumber, [command])
    return json.dumps({"response": "success", "commands": [command]})

@app.route('/<stackName>/pop/<sequenceNumber>/', methods=["GET"])
def popItem(stackName, sequenceNumber):
    stack = factory.getMapper().findByName(stackName, get_db()) or TodoStack(None, stackName);
    trash_stack = factory.getMapper().findByName(stackName + "_trash", get_db()) or TodoStack(None, stackName + "_trash");
    todo = stack.pop()
    trash_stack.push(todo);
    factory.getMapper().store(stack, get_db())
    factory.getMapper().store(trash_stack, get_db())
    command = {"command": "pop", "data": {"id": str(todo.id), "content":todo.content, "priority": todo.priority, "stackid": str(todo.stackid), "order": todo.order}};
    StackCommandDispatcher.openDispatcher(stackName).new_command(sequenceNumber, [command])
    return json.dumps({"response": "success", "commands": [command]})

@app.route('/<stackName>/moveItem/<int:fromIndex>/<int:toIndex>/<sequenceNumber>/', methods=["GET"])
def moveItem(stackName, fromIndex, toIndex, sequenceNumber):
    stack = factory.getMapper().findByName(stackName, get_db()) or TodoStack(None, stackName);
    stack.moveItem(fromIndex, toIndex);
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
        command = {"command":"update", "data":{"id": str(todo.id), "content":todo.content, "priority": todo.priority, "stackid": str(todo.stackid), "order": todo.order}};
        response["commands"].append(command)
    StackCommandDispatcher.openDispatcher(stackName).new_command(sequenceNumber, response["commands"])
    return json.dumps(response)

@app.route('/<stackName>/removeItem/<int:index>/<sequenceNumber>/', methods=["GET"])
def removeItem(stackName, index):
    stack = factory.getMapper().findByName(stackName, get_db()) or TodoStack(None, stackName);
    todos = stack.getItems(True)
    todo = todos[index]
    stack.removeItem(index);
    factory.getMapper().store(stack, get_db())
    command = {"command": "remove", "data": {"id": str(todo.id), "content":todo.content, "priority": todo.priority, "stackid": str(todo.stackid), "order": todo.order}};
    StackCommandDispatcher.openDispatcher(stackName).new_command(sequenceNumber, [command])
    return json.dumps({"response": "success", "commands": [command]})

@app.route('/<stackName>/raisePriority/<int:index>/<sequenceNumber>/', methods=["GET"])
def raisePriority(stackName, index):
    stack = factory.getMapper().findByName(stackName, get_db()) or TodoStack(None, stackName);
    todos = stack.getItems(True);
    todo = todos[index];
    todo.priority += 1;
    if todo.priority >= 5:
        todo.priority %= 5;
    factory.getMapper().store(stack, get_db())
    command = {"response": "success", "commands": [{"command": "update", "data": {"id": str(todo.id), "content":todo.content, "priority": todo.priority, "stackid": str(todo.stackid), "order": todo.order}}]};
    StackCommandDispatcher.openDispatcher(stackName).new_command(sequenceNumber, [command])
    return json.dumps({"response": "success", "commands": [command]})

@app.route('/<stackName>/fetch/<sequenceNumber>/', methods=["GET"])
def fetch(stackName, sequenceNumber):
    request_sequence_number = sequenceNumber 
    commands = StackCommandDispatcher.openDispatcher(stackName).fetch_command(request_sequence_number)
    sequenceNumbers = list()
    for x in commands:
        logging.debug(x)
        if x is not None:
            sequenceNumbers.append(x["key"])
    sequenceNumber = 0
    if len(sequenceNumbers) > 0:
        sequenceNumber = max(sequenceNumbers)

    response = make_response(json.dumps({"request_sequence_number": request_sequence_number, "command_update_sequence_number": sequenceNumber, "commands": commands}))
    return response


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

if __name__ == "__main__":
    f = open('profiler.log', 'w')
    stream = MergeStream(sys.stdout, f)
    app.config['PROFILE'] = True
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, stream)
    app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
    app.debug = True
    http = WSGIServer(('', 5000),  DebuggedApplication(app));
    http.serve_forever();
