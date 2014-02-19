from other import Todo

class EmptyStackException(Exception):
    def __init__(self):
        pass
class InvalidIndexException(Exception):
    def __init__(self, index):
        self.message = "{0} is not a invalid index".format(index)
    def __str__(self):
        return self.message
class ItemExistException(Exception):
    def __init__(self, stack, item):
        self.message = "{0} already exist in {1}".format(item, stack)
    def __str__(self):
        return self.message
class OutOfRangeException(Exception):
    def __init__(self, stack, index):
        self.message = "{0} is not in range of {1}".format(index, stack)
    def __str__(self):
        return self.message
class InvalidItemException(Exception):
    def __init__(self, item):
        self.message = "push item {0}: {1}".format(item, type(item))
    def __str__(self):
        return self.message

class Stack(list):
    def push(self, item):
        if item in self:
            raise ItemExistException(self, item)
        if item is None:
            raise InvalidItemException(item)
        self.append(item)

    def pop(self):
        if len(self) is 0:
            raise EmptyStackException()
        item = list.pop(self)
        print(item)
        return item
    def size(self):
        return len(self)

    def peek(self):
        if len(self) is 0:
            raise EmptyStackException()
        return self[-1]

    def getItems(self, reverse = False):
        if reverse:
            return self[::-1]
        else:
            return list(self)

    def removeItem(self, index):
        index = int(index)
        if index < 0:
            raise InvalidIndexException(index)
        if index >= len(self):
            raise OutOfRangeException(self, index)

        item = self[index]
        del self[index]
        print(index, item)
        return item

    def moveItem(self, fromIndex, toIndex):
        fromIndex, toIndex = int(fromIndex), int(toIndex)
        item = self.removeItem(fromIndex)
        self.insert(toIndex, item)

class TodoStack(Stack):
    def __init__(self, id, name):
        Stack.__init__(self)
        self.id = id
        self.name = name
    
    def push(self, item):
        if not isinstance(item, Todo):
            raise InvalidItemException(item)
        if item.content == "" or item.content == None:
            raise InvalidItemException(item)
        item.id = None
        Stack.push(self, item)
        item.stackid = self.id
        self.assign_order_to_todos()

    def assign_order_to_todos(self):
        enum = enumerate(self)
        for index, todo in enum:
            todo.order = index

    def moveItem(self, fromIndex, toIndex):
        Stack.moveItem(self, fromIndex, toIndex)
        self.assign_order_to_todos()

    def pop(self):
        self.peek().stackid = None
        return Stack.pop(self)
