import unittest
from nose.tools import raises
from app.libs.facade import Facade, UserNotFoundError, PasswordNotCorrectError
from app.libs.model import Base, User, Todo
from app.test.model_test import DatabaseTestCase


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

    def test_move_todo_to_trash(self):
        user = self.facade.register("username1", \
            "password1", "username@domain.name")
        for i in range(1, 9):
            todo = Todo(content=str(i), owner=user)
            self.facade.push_todo(user, todo)
        todo = Todo(content=str(0), owner=user)
        todos = sorted(self.facade.append_todo(user, todo), key=lambda todo: todo.order)
        todos = filter(lambda todo: todo.in_trash == False, todos)
        self.assertEquals("4", todos[4].content)
        self.facade.move_todo_to_trash(todo=todos[4], user=user)
        todos_after_move_one_to_trash = filter(lambda todo: todo.in_trash == False, self.facade.find_todos_by_owner(user))
        self.assertTrue(9, len(todos_after_move_one_to_trash))
        for i in range(len(todos_after_move_one_to_trash)):
            print todos_after_move_one_to_trash[i].content, i
            self.assertNotEquals("4", todos_after_move_one_to_trash[i].content)

    def test_move_todo_while_nothing_to_mvoe(self):
        user = self.facade.register("username1", \
            "password1", "username@domain.name")
        self.assertEquals(None, self.facade.move_todo(user=user, fromOrder=1, toOrder=2))

    def test_move_todo_from_high_to_low(self):
        user = self.facade.register("username1", \
            "password1", "username@domain.name")
        for i in range(10):
            todo = Todo(content=str(i), owner=user)
            self.facade.push_todo(user, todo)
        self.facade.move_todo(user=user, fromOrder=9, toOrder=1)

        query_todos = sorted(self.facade.find_todos_by_owner(user), key=lambda todo: todo.order)
        self.assertEquals(10, len(query_todos))
        self.assertEquals("0", query_todos[0].content)
        self.assertEquals("9", query_todos[1].content)
        self.assertEquals("1", query_todos[2].content)
        self.assertEquals("2", query_todos[3].content)
        self.assertEquals("3", query_todos[4].content)
        self.assertEquals("4", query_todos[5].content)
        self.assertEquals("5", query_todos[6].content)
        self.assertEquals("6", query_todos[7].content)
        self.assertEquals("7", query_todos[8].content)
        self.assertEquals("8", query_todos[9].content)

    def test_move_todo_from_low_to_high(self):
        user = self.facade.register(
            "username1",
            "password1",
            "username@domain.name")
        for i in range(10):
            todo = Todo(content=str(i), owner=user)
            self.facade.push_todo(user, todo)
        self.facade.move_todo(user=user, fromOrder=1, toOrder=9)

        query_todos = sorted(
            self.facade.find_todos_by_owner(user),
            key=lambda todo: todo.order
        )
        self.assertEquals(10, len(query_todos))
        self.assertEquals("0", query_todos[0].content)
        self.assertEquals("2", query_todos[1].content)
        self.assertEquals("3", query_todos[2].content)
        self.assertEquals("4", query_todos[3].content)
        self.assertEquals("5", query_todos[4].content)
        self.assertEquals("6", query_todos[5].content)
        self.assertEquals("7", query_todos[6].content)
        self.assertEquals("8", query_todos[7].content)
        self.assertEquals("9", query_todos[8].content)
        self.assertEquals("1", query_todos[9].content)

    def test_clean_trash(self):
        user = self.facade.register("username1", \
            "password1", "username@domain.name")
        for i in range(10):
            todo = Todo(content=str(i), owner=user)
            if i % 2 == 0:
                todo.in_trash = True
            self.facade.push_todo(user, todo)
        todos = self.facade.find_todos_by_owner(user)
        in_trash_todos = [todo for todo in todos if todo.in_trash == True]
        self.assertEquals(5, len(in_trash_todos))
        todos = self.facade.clean_trash(user)
        self.assertEquals(5, len(todos))
        for todo in todos:
            self.assertTrue(todo.order % 2 == 0)
        todos = self.facade.find_todos_by_owner(user)
        in_trash_todos = [todo for todo in todos if todo.in_trash == True]
        self.assertEquals(0, len(in_trash_todos))

    def test_remove_todo(self):
        user = self.facade.register("username1", \
            "password1", "username@domain.name")
        for i in range(10):
            todo = Todo(content=str(i), owner=user)
            self.facade.push_todo(user, todo)
        todos = sorted(self.facade.find_todos_by_owner(user), key=lambda todo: todo.order)
        return_by_move = self.facade.remove_todo(user=user, todo=todos[0])

        query_todos = sorted(self.facade.find_todos_by_owner(user), key=lambda todo: todo.order)
        self.assertEquals(9, len(query_todos))
        self.assertEquals("1", query_todos[0].content)
        self.assertEquals("2", query_todos[1].content)
        self.assertEquals("3", query_todos[2].content)
        self.assertEquals("4", query_todos[3].content)
        self.assertEquals("5", query_todos[4].content)
        self.assertEquals("6", query_todos[5].content)
        self.assertEquals("7", query_todos[6].content)
        self.assertEquals("8", query_todos[7].content)
        self.assertEquals("9", query_todos[8].content)

    def test_raise_priority(self):
        user = self.facade.register("username1", \
            "password1", "username@domain.name")
        todo = Todo(content=str(0), owner=user)
        self.facade.push_todo(user, todo)
        self.assertEquals(2, todo.priority)
        self.facade.raise_priority(user, todo)
        self.assertEquals(3, todo.priority)
        self.facade.raise_priority(user, todo)
        self.assertEquals(4, todo.priority)
        self.facade.raise_priority(user, todo)
        self.assertEquals(0, todo.priority)
        self.facade.raise_priority(user, todo)
        self.assertEquals(1, todo.priority)
        self.facade.raise_priority(user, todo)
        self.assertEquals(2, todo.priority)

    @raises(UserNotFoundError)
    def test_find_user_by_credential_while_no_users(self):
        self.facade.find_user_by_credential("username1", "password")

    @raises(PasswordNotCorrectError)
    def test_find_user_by_credential_while_password_not_correct(self):
        user = self.facade.register("username1", \
            "password1", "username@domain.name")
        self.facade.find_user_by_credential("username1", "123")

    def test_find_user_by_credential_normal(self):
        user = self.facade.register("username1", \
            "password1", "username@domain.name")
        find_user = self.facade.find_user_by_credential("username1", "password1")
        self.assertEquals(user.id, find_user.id)
