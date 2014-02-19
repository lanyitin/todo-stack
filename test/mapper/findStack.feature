Feature: findByName
    Scenario: find a stack which has no items
        Given we use mongo mapper
        When find a stack which is named aabbccdd 
        then the stack is empty 
        then clean up
    Scenario: find a stack which is not empty
        Given we use mongo mapper
        Given we already have a todo list, which is named abc and has [11,22,33]
        When find a stack which is named abc 
        then the stack is [11,22,33] 
        then clean up
