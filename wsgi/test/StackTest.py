import unittest, os, sys
sys.path.append(os.path.abspath("."))

from core import Stack

class StackTest(unittest.TestCase):
    def setUp(self):
        self.stack = Stack();
    def testPush(self):
        self.assertEqual(0, self.stack.size())
        self.stack.push(1);
        self.assertEqual(1, self.stack.size())
    
    def testCannotPushNone(self):
        self.stack.push(None);
        self.assertEqual(0, self.stack.size())
        
    def testPop(self):
        item = 1;
        self.stack.push(item);
        self.assertEquals(item, self.stack.pop())
        self.assertEquals(0, self.stack.size())

    def testPopoutTooMoreTimeShouldReturnNone(self):
        item = 1;
        self.stack.push(item);
        self.assertEquals(item, self.stack.pop())
        self.assertEquals(None, self.stack.pop())
        

    def testPushSameItemTwiceShouldWork(self):
        item = 1;
        self.stack.push(item);
        self.stack.push(item);
        self.assertEquals(2, self.stack.size())
        self.assertEquals(item, self.stack.pop())
        self.assertEquals(item, self.stack.pop())
        
    def testRemoveItem(self):
        for i in range(3):
            self.stack.push(i);

        self.stack.removeItem(1);
        self.assertEquals(2, self.stack.size())
        self.assertEquals(2, self.stack.pop())
        self.assertEquals(0, self.stack.pop())

    def testMoveItem(self):
        fromIndex = 1;
        toIndex = 3;
        for i in range(5):
            self.stack.push(i);
        
        self.stack.moveItem(fromIndex, toIndex);
        # 4 3 2 1 0
        # 4 2 1 3 0
        self.assertEquals(4, self.stack.pop());
        self.assertEquals(2, self.stack.pop());
        self.assertEquals(1, self.stack.pop());
        self.assertEquals(3, self.stack.pop());
        self.assertEquals(0, self.stack.pop());

    def testMoveItemCanBeReverse(self):
        self.testMoveItem()
        fromIndex = 1;
        toIndex = 3;
        for i in range(5):
            self.stack.push(i);
        
        self.stack.moveItem(fromIndex, toIndex);
        self.stack.moveItem(toIndex, fromIndex);
        for i in range(5):
            self.assertEquals(5 - i - 1, self.stack.pop())
