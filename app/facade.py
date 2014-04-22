# -*- coding: utf-8 -*-
from core.model import db, Todo, User, Tag
from sqlalchemy import and_, desc
from datetime import datetime

class Facade:
    def find_all_todos(self, userid):
        stack = Todo.query.filter_by(owner_user_id = userid, in_trash = False).order_by(desc(Todo.order)).all()
        trash_stack = Todo.query.filter_by(owner_user_id = userid, in_trash = True).order_by(Todo.push_date_time).all()
        return stack, trash_stack


    def find_todo_by_tag(self, userid, tagName):
        stack = Todo.query.filter_by(owner_user_id = userid, in_trash = False).filter(Todo.tags.any(name = tagName)).all()
        trash_stack = Todo.query.filter_by(owner_user_id = userid, in_trash = True).order_by(Todo.push_date_time).all()
        return stack, trash_stack


    def push_todo(self, userid, content):
        top_item = Todo.query.filter_by(owner_user_id=userid, in_trash=False).order_by(desc(Todo.order)).first()
        todo = Todo(content, userid)
        if top_item is not None:
            todo.order = top_item.order + 1
        else:
            todo.order = 0
        db.session.add(todo)
        db.session.commit()
        return todo


    def append_todo(self, userid, content):
        todo = Todo(content, userid)
        stack = Todo.query.filter_by(owner_user_id=userid, in_trash=False).order_by(Todo.order).all()
        if len(stack) > 0 and stack[0].order > 1:
            todo.order = stack[0].order - 1
        else:
            todo.order = 0
        response = []
        processed_item = todo
        db.session.add(todo)
        db.session.commit()
        response.append(todo)

        for top_item in stack:
            top_item.order = processed_item.order + 1
            db.session.add(top_item)
            response.append(top_item)
            processed_item = top_item

        db.session.commit()

        return response


    def move_todo_to_trash(self, todoid):
        top_item = Todo.query.filter_by(id=todoid).order_by(desc(Todo.order)).first()
        if top_item is not None:
            top_item.in_trash = True
            top_item.push_date_time = datetime.utcnow()
            db.session.add(top_item)
            db.session.commit()
            todo = top_item
            return todo
        else:
            return None


    def move_todo(self, userid, fromIndex, toIndex):
        stack = Todo.query.filter_by(owner_user_id = userid, in_trash = False).order_by(desc(Todo.order)).all()
        response = []
        begin = end = 0
        if (fromIndex > toIndex):
            begin = toIndex
            end = fromIndex
            fromIndex -= toIndex
            toIndex -= toIndex
        else:
            end = toIndex
            begin = fromIndex
            toIndex -= fromIndex
            fromIndex -= fromIndex

        item_slice = stack[begin:end + 1]
        order_slice = [item.order for item in item_slice]
        item_slice.insert(toIndex, item_slice.pop(fromIndex))

        for order, todo in zip(order_slice, item_slice):
            todo.order = order
            db.session.add(item)
            response.append(todo)

        db.session.commit()
        return response


    def remove_todo(self, userid, todoid):
        todo = Todo.query.filter_by(id = todoid).first()
        db.session.delete(todo)
        db.session.commit()
        tags = Tag.query.filter_by(owner_user_id=userid).all()
        tags = [tag for tag in tags if len(tag.todos) is 0]
        for tag in tags:
            db.session.delete(tag)
        db.session.commit()
        return todo


    def find_all_tag(self, userid):
        return Tag.query.filter_by(owner_user_id = userid).all()


    def clean_trash(self, userid):
        todos = Todo.query.filter_by(owner_user_id = userid, in_trash = True).all()
        response = []
        for todo in todos:
            db.session.delete(todo)
            response.append(todo)
        db.session.commit()
        tags = Tag.query.filter_by(owner_user_id=userid).all()
        tags = [tag for tag in tags if len(tag.todos) is 0]
        for tag in tags:
            db.session.delete(tag)
        db.session.commit()
        return response

    def raise_priority(self, todoid):
        todo = Todo.query.filter_by(id = todoid).first()
        todo.priority += 1
        if todo.priority >= 5:
            todo.priority %= 5
        db.session.add(todo)
        db.session.commit()
        return todo
