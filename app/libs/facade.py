from sqlalchemy.exc import IntegrityError
from .model import User, Todo
import operator


class Facade:
    '''
        all todo-manipulate method should return a list of effected(changed) todos
    '''
    def __init__(self, session, engine):
        self.session = session
        self.engine = engine

    def register(self, username, password, email):
        try:
            user = User(
                username=username,
                password=password,
                email=email,
            )
            self.session.add(user)
            self.session.commit()
            return user
        except IntegrityError:
            return None

    def find_todos_by_owner(self, owner):
        if owner.id is None:
            return None
        todos = self.session.query(Todo).filter_by(owner=owner).all()
        self.session.flush()
        return todos

    def find_todo_by_id(self, userid):
        todos = self.session.query(Todo).filter_by(id=userid).first()
        self.session.flush()
        return todos

    def push_todo(self, user, target_todo):
        ''' in order to avoiding coupling with SQLAlchemy
        I prefer not to use **sqlalchemy.sql.expression.func.max**
        '''
        todos = self.find_todos_by_owner(user)
        with self.session.no_autoflush:
            if len(todos) == 0:
                target_todo.order = 0
            else:
                order_list = [todo.order for todo in todos]
                max_order = max(order_list)
                target_todo.order = max_order + 1
            self.session.add(target_todo)
            self.session.commit()
        return [target_todo]

    def append_todo(self, user, todo):
        exists_todos = sorted(self.find_todos_by_owner(user), key=lambda exists_todo: exists_todo.order)
        exists_todos = filter(lambda todo: todo.in_trash is False, exists_todos)
        try:
            with self.session.no_autoflush:
                for exists_todo in reversed(exists_todos):
                    '''
                        the reason that I use **reversed** is avoiding IntegrityError
                    '''
                    exists_todo.order += 1
                    self.session.add(exists_todo)
                    self.session.flush()
                todo.order = 0
                self.session.add(todo)
                self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e
        return self.find_todos_by_owner(user)

    def move_todo_to_trash(self, user, todo):
        exists_todos = sorted(self.find_todos_by_owner(user), key=lambda exists_todo: exists_todo.order)
        exists_todos = filter(lambda todo: todo.in_trash is True, exists_todos)
        todo.in_trash = True
        todo.order = len(exists_todos)
        self.session.add(todo)
        self.session.commit()
        return [todo]

    def move_todo(self, user, fromOrder, toOrder):
        exists_todos = sorted(self.find_todos_by_owner(user), key=lambda exists_todo: exists_todo.order)
        exists_todos = filter(lambda todo: todo.in_trash is False, exists_todos)
        with self.session.no_autoflush:
            if fromOrder not in range(len(exists_todos)) or toOrder not in range(len(exists_todos)):
                return None
            if fromOrder > toOrder:
                self.__move_todo_template__(
                    todos=reversed(sorted([todo for todo in exists_todos], key=lambda todo: todo.order)),
                    order_cmp_op1=operator.le,
                    order_cmp_op2=operator.lt,
                    order_offset_op=operator.iadd,
                    toOrder=toOrder,
                    fromOrder=fromOrder,
                )
            elif fromOrder < toOrder:
                self.__move_todo_template__(
                    todos=sorted([todo for todo in exists_todos], key=lambda todo: todo.order),
                    order_cmp_op1=operator.ge,
                    order_cmp_op2=operator.gt,
                    order_offset_op=operator.isub,
                    toOrder=toOrder,
                    fromOrder=fromOrder,
                )

    def __move_todo_template__(self, todos, order_offset_op, order_cmp_op1, order_cmp_op2, toOrder, fromOrder):
        ''' spent too much time in iterate through list '''
        todos = [todo for todo in todos]
        target_todo = None
        for todo in todos:
            if todo.order is fromOrder:
                target_todo = todo
                break
        try:
            target_todo.order = -1
            self.session.add(target_todo)
            self.session.flush()

            for todo in todos:
                if order_cmp_op1(toOrder, todo.order) and order_cmp_op2(todo.order, fromOrder):
                    todo.order = order_offset_op(todo.order, 1)
                    self.session.add(todo)
                    self.session.flush()

            target_todo.order = toOrder
            self.session.add(target_todo)
            self.session.commit()
        except Exception as e:
            for todo in todos:
                print(todo.id, todo.order)
            print(target_todo.id, target_todo.order)
            self.session.rollback()
            raise e

    def clean_trash(self, user):
        todos = self.session.query(Todo).filter_by(owner=user, in_trash=True).all()
        for todo in todos:
            self.session.delete(todo)
        self.session.commit()
        return todos

    def remove_todo(self, user, todo):
        self.session.delete(todo)
        self.session.commit()
        return [todo]

    def raise_priority(self, user, todo):
        todo.raise_priority()
        self.session.add(todo)
        self.session.commit()
        return [todo]

    def find_user_by_credential(self, username, password):
        user = self.session.query(User).filter_by(username=username).first()
        if user is None:
            raise UserNotFoundError()
        if user.password != User.generate_password_hash(password):
            raise PasswordNotCorrectError()
        return user

    def increase_consumed_clock(self, todo):
        todo.consumed_clock += 1
        todo.consumed_clock = min(todo.required_clock + todo.extended_clock, todo.consumed_clock)
        self.session.add(todo)
        self.session.commit()
        return [todo]


    def add_extended_clock(self, todo, extended_clock):
        todo.extended_clock = max(todo.extended_clock + extended_clock, 0)
        self.session.add(todo)
        self.session.commit()
        return [todo]


class UserNotFoundError(Exception):
    pass


class PasswordNotCorrectError(Exception):
    pass
