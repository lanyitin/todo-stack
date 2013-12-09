from __future__ import print_function
import unittest, os, sys, sqlite3
sys.path.append(os.path.abspath("."))

from app.core import TodoStack
from app.core import Todo
from app.core import SqliteStackMapper


class StackMapperTest(unittest.TestCase):
    def setUp(self):
        self.stackName = "testStack"
        self.db = sqlite3.connect("test.db")
        with open('app/schema.sql', mode='r') as f:
            self.db.executescript(f.read())
            self.db.commit()
    def tearDown(self):
        cursor = self.db.cursor();
        cursor.execute("delete from stack");
        cursor.execute("delete from todo");
        cursor.execute("drop table stack");
        cursor.execute("drop table todo");
        self.db.commit();
        self.db.close()

    def testCreateNewStackOnlyIfTheStackHasNoIdAndHasAtLeastOneItem(self):
        stack = TodoStack(None, self.stackName)
        SqliteStackMapper.store(stack, self.db)
        cursor = self.db.cursor();
        rows = cursor.execute("select name from stack where name=?", (self.stackName,));
        self.assertEquals(0, len(rows.fetchall()))


        stack.push(1)
        SqliteStackMapper.store(stack, self.db)
        rows = cursor.execute("select name from stack where name=?", (self.stackName,));
        self.assertEquals(1, len(rows.fetchall()))
        self.assertEquals(1, stack.id)

    def testFindByName(self):
        stack = TodoStack(None, self.stackName);
        for i in range(5):
            stack.push(i)
        SqliteStackMapper.store(stack, self.db)
        stack = SqliteStackMapper.findByName(self.stackName, self.db)
        self.assertEquals(5, stack.size())
        i = 0;
        for item in stack.getItems(True):
            self.assertEquals(str(5 - i - 1), item.content)
            self.assertEquals(5 - i - 1, item.order)
            i += 1
        
    def testFindByNameShouldReturnNone(self):
        self.assertEquals(None, SqliteStackMapper.findByName(self.stackName, self.db))

    def testCannotHaveTwoStackWithSameName(self):
        stack = TodoStack(None, self.stackName)
        stack.push(1)
        SqliteStackMapper.store(stack, self.db)
        stack.id = None
        with self.assertRaises(Exception) as cm:
            SqliteStackMapper.store(stack, self.db)
    def testAutoStripStackNameBeforeIntertIntoTable(self):
        cursor = self.db.cursor()
        rows = cursor.execute("select name from stack where name=?", (self.stackName,));
        self.assertEquals(0, len(rows.fetchall()))
        newStackName = "    " + self.stackName;
        stack = TodoStack(None, newStackName);
        stack.push(1)
        SqliteStackMapper.store(stack, self.db)
        self.assertEquals(self.stackName, stack.name);
        rows = cursor.execute("select name from stack where name=?", (self.stackName,));
        self.assertEquals(1, len(rows.fetchall()))

    def testMoveItem(self):
        stack = TodoStack(None, self.stackName);
        for i in range(5):
            stack.push(i)
        SqliteStackMapper.store(stack, self.db)
        stack = SqliteStackMapper.findByName(self.stackName, self.db)
        stack.moveItem(0, 1)
        SqliteStackMapper.store(stack, self.db)
        
        stack = SqliteStackMapper.findByName(self.stackName, self.db)
        item = stack.pop()
        self.assertEquals("3", item.content)
        self.assertEquals(4, item.order)
        item = stack.pop()
        self.assertEquals("4", item.content)
        self.assertEquals(3, item.order)

    def testRemoveItem(self):
        stack = TodoStack(None, self.stackName);
        for i in range(5):
            stack.push(i)
        SqliteStackMapper.store(stack, self.db)
        stack = SqliteStackMapper.findByName(self.stackName, self.db)
        stack.removeItem(2)
        SqliteStackMapper.store(stack, self.db)
        stack = SqliteStackMapper.findByName(self.stackName, self.db)
        for item in stack.getItems():
            self.assertNotEquals("2", item.content)
    def testTransferTodoToOtherStack(self):
        stack = TodoStack(None, self.stackName);
        for i in range(5):
            stack.push(i)
        SqliteStackMapper.store(stack, self.db)
        stack = SqliteStackMapper.findByName(self.stackName, self.db)
        self.assertEquals(5, stack.size())
        trash_stack = TodoStack(None, self.stackName + "_trash");
        trash_stack.push(stack.pop());
        SqliteStackMapper.store(stack, self.db)
        SqliteStackMapper.store(trash_stack, self.db)
        stack = SqliteStackMapper.findByName(self.stackName, self.db)
        trash_stack = SqliteStackMapper.findByName(self.stackName + "_trash", self.db)
        self.assertEquals(4, stack.size())
        self.assertEquals(1, trash_stack.size())

    def testEmptyAStackByCallRemoveItem(self):
        stack = TodoStack(None, self.stackName);
        for i in range(5):
            stack.push(i)
        SqliteStackMapper.store(stack, self.db)
        self.assertTrue(stack.id is not None)
        for i in range(5):
            stack.pop()
        SqliteStackMapper.store(stack, self.db)
        stack = SqliteStackMapper.findByName(self.stackName, self.db)
        self.assertEquals(0, stack.size())
