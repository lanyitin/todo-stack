Feature: moveItem
    Scenario: move items in todo_stack should change the order of todo item
        Given we have a stack
        When push todo item with random attributes and content 7
        When push todo item with random attributes and content 6
        When push todo item with random attributes and content 8
        When push todo item with random attributes and content 3
        When push todo item with random attributes and content 0
        When push todo item with random attributes and content 1
        When push todo item with random attributes and content 2
        When move item from index 3 to index 6
        then the stack is [7,6,8,0,1,2,3]
