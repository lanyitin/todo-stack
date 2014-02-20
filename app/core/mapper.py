from stack import TodoStack
from other import Todo, User
from bson.objectid import ObjectId
import pymongo

class AbstractMapper:
    @classmethod
    def store(cls, stack, userid, db):
        cls.stripName(stack)
        cls.createStackOnlyIfTheStackHasNoIdAndHasAtLeastOneItem(db, stack, userid)
        cls.storeTodos(db, stack)
        cls.deletePopoutOrRemoveItem(db, stack)
    @staticmethod
    def deletePopoutOrRemoveItem(db, stack):
        pass

    @staticmethod
    def storeTodos(db, stack):
        pass

    @staticmethod
    def createStackOnlyIfTheStackHasNoIdAndHasAtLeastOneItem(db, stack, userid):
        pass

    @staticmethod
    def updateStackId(stack):
        pass
    
    @staticmethod
    def stripName(stack):
        pass

    @classmethod
    def findByNameAndUserId(cls, name, userid, db):
        pass
    

class MongoStackMapper(AbstractMapper):

    @staticmethod
    def deletePopoutOrRemoveItem(db, stack):
        if stack.size() > 0:
            id_group = [todo.id for todo in stack.getItems()]
            if len(id_group) > 0:
                for row in db.stacktodos.todos.find({"_id": {'$nin': id_group}, "stackid": stack.id}):
                    print("remove",row)
                db.stacktodos.todos.remove({"_id": {'$nin': id_group}, "stackid": stack.id})
        else:
            db.stacktodos.todos.remove({"stackid": stack.id})
            db.stacktodos.stack.remove({"_id": stack.id})


    @staticmethod
    def storeTodos(db, stack):
        for item in stack.getItems():
            if item.id is None:
                item.id = db.stacktodos.todos.insert(item.__dict__)
                db.stacktodos.todos.update({"_id": item.id}, item.__dict__)
            else:
                db.stacktodos.todos.update({"_id": item.id}, item.__dict__)

    @staticmethod
    def createStackOnlyIfTheStackHasNoIdAndHasAtLeastOneItem(db, stack, userid):
        if stack.id is None and stack.size() > 0:
            rows = list(db.stacktodos.stack.find({"name": stack.name, "userid": ObjectId(userid)}))
            if len(rows) > 0:
                raise Exception({"name": stack.name, "userid": ObjectId(userid)}, "exists")
            stack.id = db.stacktodos.stack.insert({"name": stack.name, "userid": ObjectId(userid)})
            MongoStackMapper.updateStackId(stack)

    @staticmethod
    def updateStackId(stack):
        for item in stack:
            item.stackid = stack.id

    @staticmethod
    def stripName(stack):
        if " " in stack.name:
            stack.name = stack.name.strip(' \t\n\r')


    @classmethod
    def findByNameAndUserId(cls, name, userid, db):
        rows = list(db.stacktodos.stack.find({"name": unicode(name), "userid": ObjectId(userid)}))
        if len(rows) > 0:
            row = rows[0]
            stack =  TodoStack(row["_id"], row["name"])
            rows = list(db.stacktodos.todos.find({"stackid": stack.id}).sort("order", pymongo.ASCENDING))
            for row in rows:
                if "priority" in row:
                    stack.append(Todo(id = row["_id"], content = row["content"], order = row["order"], stackid = row["stackid"], priority = row["priority"]))
                else:
                    stack.append(Todo(id = row["_id"], content = row["content"], order = row["order"], stackid = row["stackid"]))
            return stack
        else:
            raise Exception("can not find stack %s" % (name))

class UserMapper:
    @classmethod
    def register(clazz, user, db):
        rows = list(db.stacktodos.user.find({"username": user.username}))
        if len(rows) > 0:
            raise Exception("user {0} exists".format(user.username))
        user.id = db.stacktodos.user.insert({"username": user.username, "password": user.password})

    @classmethod
    def findById(clazz, id, db):
        rows = list(db.stacktodos.user.find({"_id": ObjectId(id)}))
        if len(rows) is 0:
            return None
        row = rows[0]
        return User(id = row['_id'], username = row['username'], password = row['password'], authenticated = True)

    @classmethod
    def findByUsernameAndPassword(clazz, username, password, db):
        rows = list(db.stacktodos.user.find({"username": username, "password": password}))
        if len(rows) is 0:
            return None
        row = rows[0]
        return User(id = row['_id'], username = row['username'], password = row['password'], authenticated = True)

class MapperFactory:
    def __init__(self, type):
        self.type = type
    def getMapper(self):
        if self.type == "mongo":
            return MongoStackMapper
