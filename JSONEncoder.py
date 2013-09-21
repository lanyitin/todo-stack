import json
from core import TodoStack, Todo
class StackEncoder(json.JSONEncoder):
        def default(self, obj):
                if isinstance(obj, TodoStack):
                        return {'id': obj.id, 'name': obj.name, 'items': [{'id': todo.id, 'content': todo.content, 'stackid': todo.stackid, 'order': todo.order} for todo in obj.items]}
                return json.Encoder.default(self, obj)
