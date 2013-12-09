from __future__ import print_function
import gevent
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


class StackCommandDispatcher:
    dispatchers = dict()
    @classmethod
    def openDispatcher(clazz, name):
        if not clazz.dispatchers.has_key(name):
            clazz.dispatchers[name] = StackCommandDispatcher(name)
        return clazz.dispatchers[name]

    def __init__(self, stackid):
        self.stackid = stackid
        self.cache = dict()
        self.evt = gevent.event.Event()

    def new_command(self, data):
        newNumber = self.get_max_sequence_number() + 1
        self.cache[newNumber] = {"key": newNumber, "commands": data}
        self.evt.set()
        self.evt.clear()

    def fetch_command(self, sequenceNumber):
        assert type(sequenceNumber) is int
        commands = list()
        commands += [self.cache[key] for key in self.cache if key > sequenceNumber]
        if len(commands) is 0:
            self.evt.wait(timeout = 10)
            commands += [self.cache[key] for key in self.cache if key > sequenceNumber]
        newNumber = self.get_max_sequence_number(commands);
        if newNumber < sequenceNumber:
            newNumber = sequenceNumber
        return {"request_sequence_number": sequenceNumber, "commands":commands, "command_update_sequence_number": newNumber}

    def get_max_sequence_number(self, commands = None):
        result = 0;
        if commands is None:
            commands = list(self.cache.values())
        if len(commands) > 0:
            result = max([x["key"] for x in commands])
        assert type(result) is int
        return result
