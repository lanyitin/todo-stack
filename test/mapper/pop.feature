Feature: pop
    Scenario: pop from non empty stack
        Given we use mongo mapper
        Given we already have a todo list, which is named abc and has [11,22,33]
        When find a stack which is named abc
        then pop out one item
        then the stack is [11,22] 
        then the trash stack is [33]
        then clean up
