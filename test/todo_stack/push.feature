Feature: push
    Scenario: Todo is the only one type of item that TodoStack accpeted
        Given we have a stack
        When push item 7
        then get InvalidItemException
    Scenario: change stackid of todo after pushed into stack
        Given we have a stack
        When push todo item with random attributes and content 7
        then todo's stackid is self.id
        then every thing except stackid and order are not changed
    Scenario: can't push item that content is either None or empty string
        Given we have a stack
        When push todo item with random attributes and content ""
        then get InvalidItemException
        When push todo item with random attributes and content None
        then get InvalidItemException
