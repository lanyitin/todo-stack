Feature: peek
    Scenario: can't peek an empty stack
        Given we have an empty stack
        When peek the stack
        then get an EmptyStackException
