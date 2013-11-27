from __future__ import print_function
class Stack:
    def __init__(self):
        self.items = [];

    def push(self, item):
        if item is not None:
            self.items.append(item);

    def pop(self):
        if len(self.items) is 0:
            return None;
        else:
            item = self.items.pop();
            return item

    def removeItem(self, index):
        tmpList = [];
        for i in range(index):
            tmpList.append(self.items.pop());
        item = self.items.pop();
        for i in range(len(tmpList)):
            self.items.append(tmpList.pop());
        return item;

    def moveItem(self, fromIndex, toIndex):
        item = self.removeItem(fromIndex);
        tmpList = [];
        for i in range(toIndex):
            tmpList.append(self.items.pop());
        self.push(item);
        for i in range(len(tmpList)):
            self.push(tmpList.pop());

    def size(self):
        return len(self.items);

    def peek(self):
        return self.items[-1];

    def getItems(self, reverse = False):
        if reverse:
            return self.items[::-1];
        else:
            return list(self.items);

class TodoStack(Stack):
    def __init__(self, id, name):
        Stack.__init__(self);
        self.id = id;
        self.name = name;
    
    def push(self, item):
        if not isinstance(item, Todo):
            item = Todo(content = item)
        if item.stackid is not self.id:
            item.id = None
        maxOrder = 0;
        if self.size() > 0:
            maxOrder = self.items[-1].order + 1
        item.order = maxOrder
        item.stackid = self.id
        if item.content is not None and item.content is not "":
            if not isinstance(item.content, unicode):
                item.content = unicode(item.content)
            Stack.push(self, item)

class Todo:
    def __init__(self, **argus):
        if "id" in argus:
            self.id = argus["id"];
        else:
            self.id = None;

        if "order" in argus:
            self.order = argus["order"];
        else:
            self.order = None;

        if "stackid" in argus:
            self.stackid = argus["stackid"];
        else:
            self.stackid = None;

        if "priority" in argus:
            self.priority = (argus["priority"] % 5);
        else:
            self.priority = 2;

        self.content = argus["content"];

    def __str__(self):
        return str({"id":self.id, "content":self.content, "order":self.order, "stackid":self.stackid, "priority":self.priority})
