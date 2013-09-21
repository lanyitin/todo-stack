import os, sys, json, sqlite3, base64, time

from flask import Flask, request, g, abort, redirect, url_for, render_template
from core import TodoStack, Todo, StackMapper
from JSONEncoder import StackEncoder
app = Flask(__name__)

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
def listStacks():
    url = "/" + base64.b64encode(str(time.time()));
    return redirect(url.strip(' \t\n\r') );

@app.route('/<stackName>')
def displayStack(stackName):
    stack = StackMapper.findByName(stackName, get_db()) or TodoStack(None, stackName);
    trash_stack = StackMapper.findByName(stackName + "_trash", get_db()) or TodoStack(None, stackName + "_trash");
    return render_template("display_stack.html", stack=stack, trash_stack=trash_stack);

@app.route('/<stackName>/push', methods=["POST"])
def pushItem(stackName):
    stack = StackMapper.findByName(stackName, get_db()) or TodoStack(None, stackName);
    stack.push(request.form['item'])
    StackMapper.store(stack, get_db())
    return redirect("/" + stackName)

@app.route('/<stackName>/pop', methods=["GET"])
def popItem(stackName):
    stack = StackMapper.findByName(stackName, get_db()) or TodoStack(None, stackName);
    trash_stack = StackMapper.findByName(stackName + "_trash", get_db()) or TodoStack(None, stackName + "_trash");
    trash_stack.push(stack.pop());
    StackMapper.store(stack, get_db())
    StackMapper.store(trash_stack, get_db())
    return redirect("/" + stackName);

@app.route('/<stackName>/moveItem/<int:fromIndex>/<int:toIndex>', methods=["GET"])
def moveItem(stackName, fromIndex, toIndex):
    stack = StackMapper.findByName(stackName, get_db()) or TodoStack(None, stackName);
    stack.moveItem(fromIndex, toIndex);
    StackMapper.store(stack, get_db())
    return redirect("/" + stackName);

@app.route('/<stackName>/removeItem/<int:index>', methods=["GET"])
def removeItem(stackName, index):
    stack = StackMapper.findByName(stackName, get_db()) or TodoStack(None, stackName);
    stack.removeItem(index);
    StackMapper.store(stack, get_db())
    return redirect("/" + stackName);

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

if __name__ == "__main__":
    app.run(debug = "True")
