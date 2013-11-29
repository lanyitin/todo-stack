var todoTemplate = "<div class=\"list-group-item todo container\" data-todo-priority=\"<%= todo.priority %>\" data-todo-order=\"<%= todo.order %>\" data-todo-id=\"<%= todo.id %>\"> <div class=\"col-md-1 glyphicon glyphicon-sort sort icon\"></div> <div class=\"col-md-10 content\"><%= todo.content %></div> <button class=\"delete btn btn-danger pull-right col-md-2\">Delete</button> </div>"
var compiledTodoTemplate = _.template(todoTemplate);

function showSortIcons() {
    $(".sort.icon").each(function (index, elem) {
        if ($(elem).css("display") === "none") {
            $(elem).toggle();
        }

    });
}
function hideSortIcons() {
    $(".sort.icon").each(function (index, elem) {
        if ($(elem).css("display") === "block") {
            $(elem).toggle();
        }
    });
}
function showDeleteButtons() {
    $(".delete.btn:not(.control)").each(function (index, elem) {
        if ($(elem).css("display") === "none") {
            $(elem).toggle();
        }

    });
}
function hideDeleteButtons() {
    $(".delete.btn:not(.control)").each(function (index, elem) {
        if ($(elem).css("display") === "block") {
            $(elem).toggle();
        }
    });
}
function handleResponse(response) {
    response = JSON.parse(response);
    console.log(response);
    if (response.response === "success") {
        for(var i = 0; i < response.commands.length; i++) {
            var command = response.commands[i];
            if (command.command === "push") {
                var stack = $(".stack:not(.trash)");
                var domStr = compiledTodoTemplate({todo: command.data});
                stack.prepend(domStr);
                $("#control-todo-content").val("");
                if ($(".delete.btn:not(.control):last").css("display") === "none") {
                    hideDeleteButtons();
                }
                if ($(".sort.icon:last").css("display") === "none") {
                    hideSortIcons();
                }
            } else if (command.command === "update") {
                var todoDom = $(".stack .todo[data-todo-id=" + command.data.id + "]");
                console.log(todoDom);
                todoDom.attr("data-todo-order", command.data.order);
                todoDom.attr("data-todo-priority", command.data.priority);
            } else if (command.command === "delete") {
                $(".stack .todo[data-todo-id=" + command.data.id + "]").remove();
            } else if (command.command === "pop") {
                var todo = $(".stack:not(.trash) .todo:first");
                todo.select(".delete").remove();
                todo.select(".sort").remove;
                todo.select(".priority").remove;
                $(".trash.stack").append(todo);
                if ($(".trash.stack .todo:first").css("display") === "none") {
                    hideItemsInTrashStackExceptLastNItems(2);
                }
            }
        }
    }
}

function hideItemsInTrashStackExceptLastNItems(num) {
    target = $(".trash.stack .todo:not(:nth-child(n+"+($(".trash.stack .todo").length - num + 1) +"))");
    target.each(function (index, elem) {
        if ($(elem).css("display") === "block") {
            $(elem).animate({"height": "toggle"});
        }
    });
    $("#trash_expand_collapse_btn").html("Expand");
}

function showItemsInTrashStackExceptLastNItems(num) {
    target = $(".trash.stack .todo:not(:nth-child(n+"+($(".trash.stack .todo").length - num + 1) +"))");
    target.each(function (index, elem) {
        if ($(elem).css("display") === "none") {
            $(elem).animate({"height": "toggle"});
        }
    });
    $("#trash_expand_collapse_btn").html("Collapse");
}

function initControls() {
    $(".control.pop").click(function() {
        $.ajax({
            url: "/" + window.stackName + "/pop"
        }).done(function (response) {
            handleResponse(response);
        });
    });
    $(".control.push").click(function() {
        $.ajax({
            url: "/" + window.stackName + "/push", type:"POST",
            data:{"item":$("#control-todo-content").val()}
        }).done(function (response) {
            handleResponse(response);
        });
    });
    $(".control.delete").click(function() {
        $(".delete.btn:not(.control)").toggle();
        if ($(".delete.btn:not(.control):last").css("display") === "none") {
            hideDeleteButtons();
        } else {
            showDeleteButtons();
        }
    })
    $(".control.sort").click(function() {
        if ($(".sort.icon:last").css("display") === "none") {
            showSortIcons();
        } else {
            hideSortIcons();
        }
    });
    $("#trash_expand_collapse_btn").click(function (e, thiz) {
        if ($(".trash.stack .todo:first").css("display") === "block") {
            hideItemsInTrashStackExceptLastNItems(2);
        } else {
            showItemsInTrashStackExceptLastNItems(2);
        }
    });
    $(".sortable").sortable({
        start: function ( event, ui ) {
            ui.item.data("start_pos", ui.item.index());
        },
        update: function ( event, ui) {
            var from = ui.item.data("start_pos");
            var to = ui.item.index();
            $.ajax({
                url: "/" + window.stackName + "/moveItem/" + from + "/" + to
            }).done(function (response) {
                handleResponse(response);
            });
        },
        revert: true,
        handle: ".sort.icon"
    });
}

function bindUIEventHandlerToTodoView() {
    $(".todo .priority").unbind().click(function(e) {
        var currentPriority = $(e.target).attr("data-todo-priority");
        var todoId = $(e.target).attr("data-todo-id");
        var index = $(e.target).parent().index();
        $.ajax({url: "/" + window.stackName + "/raisePriority/" + index}).done(function (){
            $(e.target).html((parseInt($(e.target).html()) + 1) % 5);
        });
    });

    $(".stack:not(.trash) .todo .delete").unbind().click(function (e){
        $.ajax({url: "/" + window.stackName + "/removeItem/" + $(e.target).parent().index()}).done(function () {
            $(e.target).parent().remove();
        });

    });
}
(function() {

    initControls();
    bindUIEventHandlerToTodoView();
    hideItemsInTrashStackExceptLastNItems(2);
    hideSortIcons();
    hideDeleteButtons();

})();
