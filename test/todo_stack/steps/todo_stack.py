from behave import *
from operator import eq
import app, random
from app.core import TodoStack, EmptyStackException, ItemExistException, InvalidIndexException, OutOfRangeException, InvalidItemException, Todo

@given(u'we have a stack')
def step_impl(context):
    context.stack = TodoStack(1, "blabla")

@when(u'pop out an item')
def step_impl(context):
    context.popoutedItem = context.stack.pop()
    print context.popoutedItem 

@when(u'push todo item with random attributes and content {item}')
def step_impl(context, item):
    if item == "\"\"":
        item = ""
    elif item == "None":
        item = None
    try:
        todoAttrs = {"content":item, "stackid":random.randrange(0, 100, 2), "id": random.randrange(100), "priority": random.randrange(5)}
        todoToPush = Todo(content = todoAttrs["content"], stackid = todoAttrs["stackid"], id = todoAttrs["id"], priority = todoAttrs["priority"])
        context.compare_todo = Todo(content = todoAttrs["content"], stackid = todoAttrs["stackid"], id = todoAttrs["id"], priority = todoAttrs["priority"])
        context.stack.push(todoToPush)
    except Exception as e:
        context.exception = e

@when(u'push item {item}')
def step_impl(context, item):
    try:
        context.stack.push(item)
    except InvalidItemException as e:
        context.exception = e
@when(u'move item from index {fromIndex} to index {toIndex}')
def step_impl(context, fromIndex, toIndex):
    context.stack.moveItem(fromIndex, toIndex)

@then(u'get InvalidItemException')
def step_impl(context):
    assert isinstance(context.exception, InvalidItemException)

@then(u'todo\'s stackid is self.id')
def step_impl(context):
    assert context.stack.peek().stackid is context.stack.id

@then(u'every thing except stackid and order are not changed')
def step_impl(context):
    assert context.stack.peek().content is context.compare_todo.content
    assert context.stack.peek().id is context.compare_todo.id
    assert context.stack.peek().priority is context.compare_todo.priority
@then(u'the stack is [{items}]')
def step_impl(context, items):
    items = items.split(",");
    items = map(str, items)
    for index, todo in enumerate(context.stack):
        assert todo.content == items[index]
        assert todo.order == index

@then(u'the pop out item\'s stackid is None')
def step_impl(context):
    assert context.popoutedItem.stackid is None
