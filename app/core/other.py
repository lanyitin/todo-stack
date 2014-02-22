from __future__ import print_function
import gevent
from gevent.event import Event

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
        self.evt = Event()

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
