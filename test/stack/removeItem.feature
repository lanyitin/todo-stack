Feature: removeItem
    Scenario: specified index is validated
        Given we have a non empty stack with items [11,42,38,40]
        When remove item at index 2
        When get items from stack
        then the items is [11,42,40]
        When get items from stack with reversed order
        then the items is [40,42,11]
    Scenario: specified index is invalidated
        Given we have a non empty stack with items [1,2,3,4]
        When remove item at index -1
        When get items from stack
        then get InvalidIndexException
    Scenario: specified index is out of range
        Given we have a non empty stack with items [1,2,3,4]
        When remove item at index 4
        When get items from stack
        then get OutOfRangeException
