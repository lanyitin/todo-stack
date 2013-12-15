Feature: size
    Scenario: size of empty stack is zero
        Given we have an empty stack
        then the size of stack is 0
    Scenario: size of non-empty stack is the number of items that stack has
        Given we have a non empty stack with items [1,2,3,4,5,6]
        then the size of stack is 6
