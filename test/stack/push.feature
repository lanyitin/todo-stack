Feature: push
    Scenario: after push an item, the size of stack should increased by 1
        Given we have a non empty stack with items [1,2,3,4,5,6]
        Given the size of stack is 6
        When push item 7
        then the size of stack is 7
        then the top item is 7

    Scenario: Every item in stack is unique
        Given we have a non empty stack with items [1,2,3,4,5,6]
        Given the size of stack is 6
        When push item 6
        then get ItemExistException with message "6 already exist in [1, 2, 3, 4, 5, 6]"
    Scenario: can not push None
        Given we have a non empty stack with items [1,2,3,4,5,6]
        When push item None
        then get InvalidItemException
