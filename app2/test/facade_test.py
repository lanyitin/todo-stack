import unittest
from app2.libs.facade import Facade
from app2.libs.model import Base, User, Todo
from app2.test.model_test import DatabaseTestCase

class facade_test(DatabaseTestCase):
    def setUp(self):
        super(facade_test, self).setUp()
        self.facade = Facade(engine=self.engine, session=self.session)

    def test_register(self):
        user = self.facade.register("username1", \
            "password1", "username@domain.name")
        self.assertTrue(user is not None)

    def test_find_todos_by_owner(self):
        user = self.facade.register("username1", \
            "password1", "username@domain.name")
        todos = self.facade.find_todos_by_owner(user)
        self.assertTrue(todos is not None)

    def test_find_todos_by_owner(self):
        user = User(
                username="username1",
                password="password1",
                email="username@domain.name",
            )
        self.assertTrue(user.id is None)
        todos = self.facade.find_todos_by_owner(user)
        self.assertTrue(todos is None)

    def test_find_todo_by_id(self):
        user = User(
                username="username1",
                password="password1",
                email="username@domain.name",
            )
        self.session.add(user)
        todo = Todo(content="Hello1", owner=user)
        self.session.add(todo)
        self.session.commit()
        self.assertTrue(self.facade.find_todo_by_id(todo.id) is not None)
    def test_find_todo_by_id_should_return_none_if_todo_not_exists(self):
        user = User(
                username="username1",
                password="password1",
                email="username@domain.name",
            )
        self.session.add(user)
        todo = Todo(content="Hello2", owner=user)
        self.session.add(todo)
        self.session.commit()
        self.assertTrue(self.facade.find_todo_by_id(todo.id + 1) is None)

    def test_push_while_stack_is_empty(self):
        user = self.facade.register("username1", \
            "password1", "username@domain.name")
        todo = Todo(content="Hello3", owner=user)
        self.assertTrue(todo.id is None)
        self.facade.push_todo(user, todo)
        self.assertEquals(0, todo.order)

    def test_push_the_second_todo_s_order_is_1(self):
        user = self.facade.register("username1", \
            "password1", "username@domain.name")
        todo = Todo(content="Hello3", owner=user)
        self.assertTrue(todo.id is None)
        self.facade.push_todo(user, todo)
        self.assertEquals(0, todo.order)
        todo = Todo(content="World", owner=user)
        self.facade.push_todo(user, todo)
        self.assertEquals(1, todo.order)

    def test_append(self):
        user = self.facade.register("username1", \
            "password1", "username@domain.name")
        for i in range(1, 11):
            todo = Todo(content=str(i), owner=user)
            self.facade.push_todo(user, todo)
        todo = Todo(content=str(0), owner=user)
        todos = sorted(self.facade.append_todo(user, todo), key=lambda todo: todo.order)
        for i in range(11):
            self.assertEquals(str(i), todos[i].content)
            self.assertEquals(i, todos[i].order)
