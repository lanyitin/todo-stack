Feature: moveItem
    Scenario: specified indexes is validated and fromIndex < toIndex
        Given we have a non empty stack with items [1,2,3,4]
        When move item from index 2 to index 3
        When get items from stack
        then the items is [1,2,4,3]
    Scenario: specified indexes is validated and fromIndex > toIndex
        Given we have a non empty stack with items [1,2,3,4]
        When move item from index 3 to index 0
        When get items from stack
        then the items is [4,1,2,3]
