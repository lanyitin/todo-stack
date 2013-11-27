import os, sys, json, sqlite3, base64, time, pymongo, json

from flask import Flask, request, g, abort, redirect, url_for, render_template
from core import TodoStack, Todo
from Mappers import MapperFactory
app = Flask(__name__)
factory = MapperFactory("mongo")

def init_db():
	with app.app_context():
		db = get_db()
		with app.open_resource('schema.sql', mode='r') as f:
			db.executescript(f.read())
			db.commit()
def get_db():
	db = getattr(g, '_database', None)
	if db is None:
		# db = g._database = sqlite3.connect("db");
		mongo_con = pymongo.Connection(os.environ['OPENSHIFT_MONGODB_DB_HOST'], int(os.environ['OPENSHIFT_MONGODB_DB_PORT']))

		mongo_db = mongo_con[os.environ['OPENSHIFT_APP_NAME']]
		mongo_db.authenticate(os.environ['OPENSHIFT_MONGODB_DB_USERNAME'], os.environ['OPENSHIFT_MONGODB_DB_PASSWORD'])
		db = mongo_db
	return db

# init_db();

@app.route('/')
def createStack():
	url = "/" + base64.b64encode(str(time.time()));
	return redirect(url.strip(' \t\n\r%\\') );

@app.route('/<stackName>')
def displayStack(stackName):
	stack = factory.getMapper().findByName(stackName, get_db()) or TodoStack(None, stackName);
	trash_stack = factory.getMapper().findByName(stackName + "_trash", get_db()) or TodoStack(None, stackName + "_trash");
	return render_template("display_stack.html", stack=stack, trash_stack=trash_stack);

@app.route('/<stackName>/push', methods=["POST"])
def pushItem(stackName):
	stack = factory.getMapper().findByName(stackName, get_db()) or TodoStack(None, stackName);
	stack.push(request.form['item'])
	factory.getMapper().store(stack, get_db())
	todo = stack.peek()
	return json.dumps({"response": "success", "commands": [{"command": "push", "data": {"id": str(todo.id), "content":todo.content, "priotiry": todo.priority, "stackid": str(todo.stackid), "order": todo.order}}]})

@app.route('/<stackName>/pop', methods=["GET"])
def popItem(stackName):
	stack = factory.getMapper().findByName(stackName, get_db()) or TodoStack(None, stackName);
	trash_stack = factory.getMapper().findByName(stackName + "_trash", get_db()) or TodoStack(None, stackName + "_trash");
	todo = stack.pop()
	trash_stack.push(todo);
	factory.getMapper().store(stack, get_db())
	factory.getMapper().store(trash_stack, get_db())
	return json.dumps({"response": "success", "commands": [{"command": "pop", "data": {"id": str(todo.id), "content":todo.content, "priotiry": todo.priority, "stackid": str(todo.stackid), "order": todo.order}}]})

@app.route('/<stackName>/moveItem/<int:fromIndex>/<int:toIndex>', methods=["GET"])
def moveItem(stackName, fromIndex, toIndex):
	stack = factory.getMapper().findByName(stackName, get_db()) or TodoStack(None, stackName);
	stack.moveItem(fromIndex, toIndex);
	factory.getMapper().store(stack, get_db())
        todos = stack.getItems(True)
	response = ({"response": "success", "commands": []})
	begin = end = 0
	if (fromIndex > toIndex):
	    begin = toIndex
	    end = fromIndex
	else:
	    end = toIndex
	    begin = fromIndex
	for i in range(begin, end + 1):
            todo = todos[i]
	    response["commands"].append({"command":"update", "data":{"id": str(todo.id), "content":todo.content, "priotiry": todo.priority, "stackid": str(todo.stackid), "order": todo.order}})
        return json.dumps(response)

@app.route('/<stackName>/removeItem/<int:index>', methods=["GET"])
def removeItem(stackName, index):
	stack = factory.getMapper().findByName(stackName, get_db()) or TodoStack(None, stackName);
        todos = stack.getItems(True)
        todo = todos[index]
	stack.removeItem(index);
	factory.getMapper().store(stack, get_db())
	return json.dumps({"response": "success", "commands": [{"command": "remove", "data": {"id": str(todo.id), "content":todo.content, "priotiry": todo.priority, "stackid": str(todo.stackid), "order": todo.order}}]})

@app.route('/<stackName>/raisePriority/<int:index>', methods=["GET"])
def raisePriority(stackName, index):
	stack = factory.getMapper().findByName(stackName, get_db()) or TodoStack(None, stackName);
	todos = stack.getItems(True);
	todo = todos[index];
	todo.priority += 1;
	if todo.priority >= 5:
		todo.priority %= 5;
	factory.getMapper().store(stack, get_db())
	return json.dumps({"response": "success", "commands": [{"command": "update", "data": {"id": str(todo.id), "content":todo.content, "priotiry": todo.priority, "stackid": str(todo.stackid), "order": todo.order}}]})


@app.teardown_appcontext
def close_connection(exception):
	db = getattr(g, '_database', None)
	if db is not None:
		db.close()

if __name__ == "__main__":
	app.run(debug = "True")
