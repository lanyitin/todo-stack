from __future__ import print_function
import unittest, os, sys, sqlite3
sys.path.append(os.path.abspath("."))

from app.core import TodoStack, Stack
from app.core import Todo

class TodoStackTest(unittest.TestCase):
    def setUp(self):
        self.stackName = "testStack"
        self.stack = TodoStack(0, self.stackName)
    
    def testPushNonTodoObjectShouldConvertToTodo(self):
        self.stack.push(1);
        self.assertTrue(isinstance(self.stack.pop(), Todo));

    def testCannotPushNoneNorEmptyString(self):
        self.stack.push(None);
        self.assertEquals(0, self.stack.size());
        self.stack.push("");
        self.assertEquals(0, self.stack.size());
        
    def testPushItemShouldAssignBiggestOrderToItem(self):
        for i in range(10):
            theItem = Todo(content = i)
            self.stack.push(theItem)

        currentOrder = 9999
        content = 9
        while self.stack.size() > 0:
            item = self.stack.pop()
            self.assertTrue(item.order < currentOrder);
            self.assertEquals(str(content), item.content);
            currentOrder = item.order
            content -= 1

    def testPushItemShouldAssignStackid(self):
        for i in range(5):
            self.stack.push(i)

        while self.stack.size() > 0:
            self.assertEquals(self.stack.id, self.stack.pop().stackid);
