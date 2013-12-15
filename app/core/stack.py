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

class Stack(list):
    def push(self, item):
        print item, self, item in self
        if item in self:
            raise ItemExistException(self, item)
        if item is not None:
            self.append(item)

    def pop(self):
        if len(self) is 0:
            raise EmptyStackException()
        item = list.pop(self)
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
        if index < 0:
            raise InvalidIndexException(index)
        if index >= len(self):
            raise OutOfRangeException(self, index)

        item = self[index]
        del self[index]
        return item

    def moveItem(self, fromIndex, toIndex):
        item = self.removeItem(fromIndex)
        print "item from index {0}: {1}".format(fromIndex, item)
        print "insert at index {0}".format(toIndex)
        self.insert(toIndex, item)

class TodoStack(Stack):
    def __init__(self, id, name):
        Stack.__init__(self)
        self.id = id
        self.name = name
    
    def push(self, item):
        if not isinstance(item, Todo):
            item = Todo(content = item)
        if item.stackid is not self.id:
            item.id = None
        maxOrder = 0
        if self.size() > 0:
            maxOrder = self[-1].order + 1
        item.order = maxOrder
        item.stackid = self.id
        if item.content is not None and item.content is not "":
            if not isinstance(item.content, unicode):
                item.content = unicode(item.content)
            Stack.push(self, item)
