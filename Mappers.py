from core import TodoStack, Todo
import logging
class SqliteStackMapper:
	@classmethod
	def store(cls, stack, db):
		SqliteStackMapper.stripName(stack);
		SqliteStackMapper.insertNewStackOnlyIfTheStackHasNoIdAndHasAtLeastOneItem(db, stack);
		SqliteStackMapper.storeTodos(db, stack);
		SqliteStackMapper.deletePopoutOrRemoveItem(db, stack);

	@staticmethod
	def deletePopoutOrRemoveItem(db, stack):
		if stack.size() > 0:
			id_group = [str(todo.id) for todo in stack.getItems() if todo.id is not None]
			if len(id_group) > 0:
				id_group = ",".join(id_group)
				cursor = db.cursor().execute("delete from todo where id not in (%s) and stackid=%d" % (id_group, stack.id));
				db.commit();
			else:
				logging.debug(stack.id)
				cursor = db.cursor().execute("delete from todo where stackid=%d" % (stack.id,));
				db.commit();


	@staticmethod
	def storeTodos(db, stack):
		for item in stack.getItems():
			update_items = []
			if item.id is None:
				cursor = db.cursor().execute("insert into todo (content, `order`, stackid, priority) values (?, ?, ?, ?)", (item.content, item.order, item.stackid, item.priority));
				item.id = cursor.lastrowid;
			else:
				cursor = db.cursor().execute("update todo set content=?, `order`=?, stackid=?, priority=? where id=?", (item.content, item.order, item.stackid, item.priority, item.id));
			db.commit();

	@staticmethod
	def insertNewStackOnlyIfTheStackHasNoIdAndHasAtLeastOneItem(db, stack):
		if stack.id is None and stack.size() > 0:
			cursor = db.cursor().execute("insert into stack (name) values (?)", (stack.name,));
			db.commit();
			stack.id = cursor.lastrowid;
			SqliteStackMapper.updateStackId(stack);

	@staticmethod
	def updateStackId(stack):
		for item in stack.items:
			item.stackid = stack.id;

	@staticmethod
	def stripName(stack):
		if " " in stack.name:
			stack.name = stack.name.strip(' \t\n\r');


	@classmethod
	def findByName(cls, name, db):
		cursor = db.cursor();
		rows = cursor.execute("select * from stack where name=?", (name,));
		row = rows.fetchone();
		if row is None:
			return None;
		else:
			stack =  TodoStack(row[0], row[1]);
			cursor = db.cursor();
			rows = cursor.execute("select * from todo where stackid=? order by `order` asc", (stack.id,));
			for row in rows.fetchall():
				stack.items.append(Todo(id = row[0], content = row[1], order = row[2], stackid = row[3], priority = row[4]));
			return stack;

class MongoStackMapper:
	@classmethod
	def store(cls, stack, db):
		MongoStackMapper.stripName(stack);
		MongoStackMapper.insertNewStackOnlyIfTheStackHasNoIdAndHasAtLeastOneItem(db, stack);
		MongoStackMapper.storeTodos(db, stack);
		MongoStackMapper.deletePopoutOrRemoveItem(db, stack);

	@staticmethod
	def deletePopoutOrRemoveItem(db, stack):
		if stack.size() > 0:
			id_group = [todo.id for todo in stack.getItems() if todo.id is not None]
			if len(id_group) > 0:
				db.stacktodos.todos.remove({"_id": {'$nin': id_group}, "stackid": stack.id})
		else:
				db.stacktodos.todos.remove({"stackid": stack.id})


	@staticmethod
	def storeTodos(db, stack):
		for item in stack.getItems():
			if item.id is None:
				item.id = db.stacktodos.todos.insert(item.__dict__)
			else:
				db.stacktodos.todos.update({"_id": item.id}, item.__dict__)

	@staticmethod
	def insertNewStackOnlyIfTheStackHasNoIdAndHasAtLeastOneItem(db, stack):
		if stack.id is None and stack.size() > 0:
			stack.id = db.stacktodos.stack.insert({"name": stack.name});
			SqliteStackMapper.updateStackId(stack);

	@staticmethod
	def updateStackId(stack):
		for item in stack.items:
			item.stackid = stack.id;

	@staticmethod
	def stripName(stack):
		if " " in stack.name:
			stack.name = stack.name.strip(' \t\n\r');


	@classmethod
	def findByName(cls, name, db):
		rows = list(db.stacktodos.stack.find({"name": name}))
		if len(rows) is 0:
			return None;
		else:
			row = rows[0]
			stack =  TodoStack(row["_id"], row["name"]);
			rows = list(db.stacktodos.todos.find({"stackid": stack.id}))
			for row in rows:
                                if "priority" in row:
                                    stack.items.append(Todo(id = row["_id"], content = row["content"], order = row["order"], stackid = row["stackid"], priority = row["priority"]));
                                else:
                                    stack.items.append(Todo(id = row["_id"], content = row["content"], order = row["order"], stackid = row["stackid"]));
			return stack;


class MapperFactory:
	def __init__(self, type):
		self.type = type
	def getMapper(self):
		if self.type is "mongo":
			return MongoStackMapper
		elif self.type is "sqlite":
			return SqliteStackMapper
