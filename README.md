# News
+ Support collaboration now1

# Main Idea
Manage the todo in stack-way.

# How to use?
You should push anything as soon as it flashed in your mind. To organize your todos, you can drag and drop to sort these todos. After your task has done, click on the *Pop* button to move your todo to *trash stack*. 

# Import
This is an *experimental* todos management tools, which means there is no guarantee that this tool can make you life better!

# Current State
+ We are in features defining state, so feel free to tell me your idea.
+ ~~Each stack is stored as a file, and each todo is stored as a line in file.~~
+ You can create your stack by appending by the end of URL i.e http://stack-todos.lanyitin.tw/$stackName.
+ Every stack, **including trash stack**, is **public**, http://stack-todos.lanyitin.tw/$stackName_trash for visit the trash stack.
+ For now, this project is hosted on Openshift.
+ The online version is using MongoDB as storage, you can switch to sqlite3 for personaly usage by changing __MapperFactory__'s parameter.

# We may add following features in future
+ Disqus integration for each todo
+ add timestamp to each todo
