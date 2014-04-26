from sqlalchemy.exc import IntegrityError
from app2.libs.model import User, Todo

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
        return self.session.query(Todo).filter_by(owner=owner).all()

    def find_todo_by_id(self, id):
        return self.session.query(Todo).filter_by(id=id).first()
    
    def push_todo(self, user, todo):
        ''' in order to avoiding coupling with SQLAlchemy
        I prefer not to use **sqlalchemy.sql.expression.func.max**
        '''
        todos = self.find_todos_by_owner(user)
        if len(todos) == 0:
            todo.order = 0
        else:
            order_list = [todo.order for todo in todos]
            max_order = max(order_list)
            todo.order = max_order + 1
        self.session.add(todo)
        self.session.commit()
        return [todo]

    def append_todo(self, user, todo):
        for exists_todo in reversed(sorted(self.find_todos_by_owner(user), key=lambda exists_todo: exists_todo.order)):
            '''
                the reason that I use **reversed** is avoiding IntegrityError
            '''
            exists_todo.order += 1
            self.session.add(exists_todo)
            self.session.commit()

        todo.order = 0
        self.session.add(todo)
        self.session.commit()
        return self.find_todos_by_owner(user)
