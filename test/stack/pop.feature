Feature: pop out an item
    Scenario: pop out an item from empty stack
        Given we have an empty stack
        When pop out an item
        then get an EmptyStackException
    Scenario: pop from a non-empty stack
        Given we have a non empty stack with items [1,2,3,4]
        When pop out an item
        then the pop out item is 4
