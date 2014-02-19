from __future__ import print_function
import gevent

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

class User:
    def __init__(self, **argus):
        self.__is_authenticated__ = argus['authenticated'] or False
        self.id = unicode(argus['id'])
        self.username = argus['username']
        self.password = argus['password']

    # used by flask-login
    def is_authenticated(self):
        return self.__is_authenticated__

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id
