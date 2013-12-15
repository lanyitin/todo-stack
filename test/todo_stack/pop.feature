Feature: pop
    Scenario: the stackid will be set to None after pop out
        Given we have a stack
        When push todo item with random attributes and content 7
        When push todo item with random attributes and content 6
        When push todo item with random attributes and content 8
        When push todo item with random attributes and content 3
        When push todo item with random attributes and content 0
        When push todo item with random attributes and content 1
        When push todo item with random attributes and content 2
        When pop out an item
        then the pop out item's stackid is None
