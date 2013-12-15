from behave import *
from operator import eq
import app, difflib
from app.core import Stack, EmptyStackException, ItemExistException, InvalidIndexException, OutOfRangeException

@given(u'we have an empty stack')
def step_impl(context):
    context.stack = Stack()
    assert context.stack.size() is 0

@when(u'pop out an item')
def step_impl(context):
    try:
        context.popoutItem = context.stack.pop()
    except EmptyStackException as e:
        context.exception = e

@then(u'get an EmptyStackException')
def step_impl(context):
    assert isinstance(context.exception, EmptyStackException)

@given(u'we have a non empty stack with items [{items}]')
def step_impl(context, items):
    items = items.split(",")
    items = map(int, items)
    context.stack = Stack()
    for item in items:
        context.stack.push(item)

@then(u'the pop out item is {item}')
def step_impl(context, item):
    item = int(item)
    print item,context.popoutItem
    assert context.popoutItem is item

@then(u'the size of stack is {size}')
@given(u'the size of stack is {size}')
def step_impl(context, size):
    assert context.stack.size() is int(size)

@when(u'push item {item}')
def step_impl(context, item):
    item = int(item)
    try:
        context.stack.push(item)
    except Exception as e:
        context.exception = e

@then(u'the top item is {item}')
def step_impl(context, item):
    item = int(item)
    assert context.stack.peek() is item

@when(u'peek the stack')
def step_impl(context):
    try:
        context.peekedItem = context.stack.peek()
    except EmptyStackException as e:
        context.exception = e

@when(u'get items from stack')
def step_impl(context):
    context.items = context.stack.getItems()

@when(u'get items from stack with reversed order')
def step_impl(context):
    context.items = context.stack.getItems(True)

@then(u'the size of items is {size}')
def step_impl(context, size):
    assert len(context.items) is int(size)

@then(u'the items is [{items}]')
def step_impl(context, items):
    items = items.split(",")
    items = map(int, items)
    assert any(map(eq, context.items, items))

@then(u'get ItemExistException with message "{message}"')
def step_impl(context, message):
    assert isinstance(context.exception, ItemExistException)
    assert context.exception.message == message

@when(u'remove item at index {index}')
def step_imple(context, index):
    index = int(index)
    try:
        context.stack.removeItem(index)
    except (InvalidIndexException, OutOfRangeException) as e:
        context.exception = e

@then(u'get InvalidIndexException')
def step_imple(context):
    assert isinstance(context.exception, InvalidIndexException)
@then(u'get OutOfRangeException')
def step_imple(context):
    assert isinstance(context.exception, OutOfRangeException)

@when(u'move item from index {fromIndex} to index {toIndex}')
def step_imple(context, fromIndex , toIndex):
    fromIndex ,toIndex = int(fromIndex), int(toIndex)
    context.stack.moveItem(fromIndex, toIndex)
    print context.stack
