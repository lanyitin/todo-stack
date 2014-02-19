from behave import *
from operator import eq
import app, random
from app.core import TodoStack, EmptyStackException, ItemExistException, InvalidIndexException, OutOfRangeException, InvalidItemException, Todo, MapperFactory
import pymongo, os

mongo_con = pymongo.Connection(os.environ['OPENSHIFT_MONGODB_DB_HOST'], int(os.environ['OPENSHIFT_MONGODB_DB_PORT']))

mongo_db = mongo_con[os.environ['OPENSHIFT_APP_NAME']]
mongo_db.authenticate(os.environ['OPENSHIFT_MONGODB_DB_USERNAME'], os.environ['OPENSHIFT_MONGODB_DB_PASSWORD'])
db = mongo_db

@Given(u'we use {db_type} mapper')
def step_impl(context, db_type):
    factory = MapperFactory(str(db_type))
    context.mapper = factory.getMapper()

@when(u'find a stack which is named {name}')
def step_impl(context, name):
    context.name = name
    try:
        context.stack = context.mapper.findByName(name, db)
    except Exception as e:
        context.stack = TodoStack(None, name)
    assert context.stack.name == name


@then(u'the stack is [{items}]')
def step_impl(context, items):
    items = items.split(",");
    items = map(str, items)
    context.stack = context.mapper.findByName(context.stack.name, db)
    for index, todo in enumerate(context.stack):
        print(todo.content, unicode(items[index]))
        assert todo.content == unicode(items[index])
        print(todo.order, index)
        assert todo.order == index

@then(u'the trash stack is [{items}]')
def step_impl(context, items):
    items = items.split(",");
    items = map(str, items)
    try:
        trash_stack = context.mapper.findByName(context.stack.name + "_trash", db)
    except Exception:
        trash_stack = TodoStack(None, context.stack.name + "_trash")
    assert trash_stack.size() > 0
    for index, todo in enumerate(trash_stack):
        print(todo.content, unicode(items[index]))
        assert todo.content == unicode(items[index])
        print(todo.order, index)
        assert todo.order == index

@then(u'the stack is empty')
def step_impl(context):
    assert len(context.stack) is 0

@then(u'pop out one item')
def step_impl(context):
    length = len(context.stack)
    item = context.stack.pop()
    context.mapper.store(context.stack,db)
    try:
        trash_stack = context.mapper.findByName(context.stack.name + "_trash", db)
    except Exception:
        trash_stack = TodoStack(None, context.stack.name + "_trash")

    trash_stack.push(item)
    context.mapper.store(trash_stack,db)
    assert length is len(context.stack) + 1

@then(u'clean up')
def step_impl(context):
    db.stacktodos.todos.remove({"stackid": context.stack.id})
    db.stacktodos.stack.remove({"_id": context.stack.id})
    db.stacktodos.stack.remove({"name": context.name})
    db.stacktodos.stack.remove({"name": context.name + "_trash"})

@Given(u'we already have a todo list, which is named {name} and has [{items}]')
def step_impl(context, name, items):
    items = items.split(",");
    items = map(str, items)
    stackid = db.stacktodos.stack.insert({"name": name})
    for index, text in enumerate(items):
        todo = Todo(stackid = stackid, content = items[index], order = index)
        db.stacktodos.todos.insert(todo.__dict__)
    context.stack = context.mapper.findByName(name, db)
    print(stackid, context.stack.id)
    assert stackid == context.stack.id
