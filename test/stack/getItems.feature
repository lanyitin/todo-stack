Feature: getItems
    Scenario: get items from empty stack
        Given we have an empty stack
        When get items from stack
        then the size of items is 0
    Scenario: get items from empty stack with reversed order
        Given we have an empty stack
        When get items from stack with reversed order
        then the size of items is 0
    Scenario: get items from non-empty stack
        Given we have a non empty stack with items [1,3,2,4]
        When get items from stack
        then the size of items is 4
        then the items is [1,3,2,4]
    Scenario: get items from non-empty stack with reversed order
        Given we have a non empty stack with items [1,3,2,4]
        When get items from stack with reversed order
        then the size of items is 4
        then the items is [4,2,3,1]
