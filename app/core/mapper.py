from stack import TodoStack
from other import Todo

class AbstractMapper:
    @classmethod
    def store(cls, stack, db):
        cls.stripName(stack)
        cls.createStackOnlyIfTheStackHasNoIdAndHasAtLeastOneItem(db, stack)
        cls.storeTodos(db, stack)
        cls.deletePopoutOrRemoveItem(db, stack)
    @staticmethod
    def deletePopoutOrRemoveItem(db, stack):
        pass

    @staticmethod
    def storeTodos(db, stack):
        pass

    @staticmethod
    def createStackOnlyIfTheStackHasNoIdAndHasAtLeastOneItem(db, stack):
        pass

    @staticmethod
    def updateStackId(stack):
        pass
    
    @staticmethod
    def stripName(stack):
        pass

    @classmethod
    def findByName(cls, name, db):
        pass
    

class SqliteStackMapper(AbstractMapper):

    @staticmethod
    def deletePopoutOrRemoveItem(db, stack):
        if stack.size() > 0:
            id_group = [str(todo.id) for todo in stack.getItems() if todo.id is not None]
            if len(id_group) > 0:
                id_group = ",".join(id_group)
                cursor = db.cursor().execute("delete from todo where id not in (%s) and stackid=%d" % (id_group, stack.id))
                db.commit()
            else:
                cursor = db.cursor().execute("delete from todo where stackid=%d" % (stack.id,))
                db.commit()
        else:
            if stack.id is not None:
                cursor = db.cursor().execute("delete from todo where stackid=%d" % (stack.id,))
                db.commit()

    @staticmethod
    def storeTodos(db, stack):
        for item in stack.getItems():
            update_items = []
            if item.id is None:
                cursor = db.cursor().execute("insert into todo (content, `order`, stackid, priority) values (?, ?, ?, ?)", (item.content, item.order, item.stackid, item.priority))
                item.id = cursor.lastrowid
            else:
                cursor = db.cursor().execute("update todo set content=?, `order`=?, stackid=?, priority=? where id=?", (item.content, item.order, item.stackid, item.priority, item.id))
            db.commit()

    @staticmethod
    def createStackOnlyIfTheStackHasNoIdAndHasAtLeastOneItem(db, stack):
        if stack.id is None and stack.size() > 0:
            cursor = db.cursor().execute("insert into stack (name) values (?)", (stack.name,))
            db.commit()
            stack.id = cursor.lastrowid
            SqliteStackMapper.updateStackId(stack)

    @staticmethod
    def updateStackId(stack):
        for item in stack:
            item.stackid = stack.id

    @staticmethod
    def stripName(stack):
        if " " in stack.name:
            stack.name = stack.name.strip(' \t\n\r')


    @classmethod
    def findByName(cls, name, db):
        cursor = db.cursor()
        rows = cursor.execute("select * from stack where name=?", (name,))
        row = rows.fetchone()
        if row is not None:
            stack =  TodoStack(row[0], row[1])
            cursor = db.cursor()
            rows = cursor.execute("select * from todo where stackid=? order by `order` asc", (stack.id,))
            for row in rows.fetchall():
                stack.append(Todo(id = row[0], content = row[1], order = row[2], stackid = row[3], priority = row[4]))
            return stack
        else:
            raise Exception("can not find stack %s" % (name))
class MongoStackMapper(AbstractMapper):

    @staticmethod
    def deletePopoutOrRemoveItem(db, stack):
        print stack.__dict__
        if stack.size() > 0:
            id_group = [todo.id for todo in stack.getItems() if todo.id is not None]
            if len(id_group) > 0:
                db.stacktodos.todos.remove({"_id": {'$nin': id_group}, "stackid": stack.id})
        else:
            db.stacktodos.todos.remove({"stackid": stack.id})


    @staticmethod
    def storeTodos(db, stack):
        print stack.__dict__
        for item in stack.getItems():
            if item.id is None:
                item.id = db.stacktodos.todos.insert(item.__dict__)
            else:
                db.stacktodos.todos.update({"_id": item.id}, item.__dict__)

    @staticmethod
    def createStackOnlyIfTheStackHasNoIdAndHasAtLeastOneItem(db, stack):
        print stack.__dict__
        if stack.id is None and stack.size() > 0:
            stack.id = db.stacktodos.stack.insert({"name": stack.name})
            SqliteStackMapper.updateStackId(stack)

    @staticmethod
    def updateStackId(stack):
        print stack.__dict__
        for item in stack:
            item.stackid = stack.id

    @staticmethod
    def stripName(stack):
        print stack.__dict__
        if " " in stack.name:
            stack.name = stack.name.strip(' \t\n\r')


    @classmethod
    def findByName(cls, name, db):
        rows = list(db.stacktodos.stack.find({"name": unicode(name)}))
        for row in rows:
            print row
        if len(rows) > 0:
            row = rows[0]
            stack =  TodoStack(row["_id"], row["name"])
            rows = list(db.stacktodos.todos.find({"stackid": stack.id}))
            for row in rows:
                if "priority" in row:
                    stack.append(Todo(id = row["_id"], content = row["content"], order = row["order"], stackid = row["stackid"], priority = row["priority"]))
                else:
                    stack.append(Todo(id = row["_id"], content = row["content"], order = row["order"], stackid = row["stackid"]))
            return stack
        else:
            raise Exception("can not find stack %s" % (name))


class MapperFactory:
    def __init__(self, type):
        self.type = type
    def getMapper(self):
        if self.type == "mongo":
            return MongoStackMapper
        elif self.type == "sqlite":
            return SqliteStackMapper
        else:
            raise Exception("not support type: " + self.type)
