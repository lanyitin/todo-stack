# News
+ Support collaboration now!

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
+ For now, this project is hosted on Heroku.
+ The online version is using MongoDB as storage, you can switch to sqlite3 for personaly usage by changing __MapperFactory__'s parameter.

# We may add following features in future
+ Disqus integration for each todo
+ add timestamp to each todo

# License
> Copyright (c) 2013, 2014
>      The Lan, Yi-Tin.  All rights reserved.
>
> Redistribution and use in source and binary forms, with or without
> modification, are permitted provided that the following conditions
> are met:
> 1. Redistributions of source code must retain the above copyright
>    notice, this list of conditions and the following disclaimer.
> 2. Redistributions in binary form must reproduce the above copyright
>    notice, this list of conditions and the following disclaimer in the
>    documentation and/or other materials provided with the distribution.
> 3. All advertising materials mentioning features or use of this software
>    must display the following acknowledgement:
>      This product includes software developed by the University of
>      California, Berkeley and its contributors.
> 4. Neither the name of the University nor the names of its contributors
>    may be used to endorse or promote products derived from this software
>    without specific prior written permission.
>
> THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS'' AND
> ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
> IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
> ARE DISCLAIMED.  IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE
> FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
> DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
> OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
> HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
> LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
> OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
> SUCH DAMAGE.
