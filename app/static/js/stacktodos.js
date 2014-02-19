var sequenceNumber;

function getSequenceNumber() {
    return sequenceNumber;
}
function setSequenceNumber(n) {
    sequenceNumber = n;
}
var todoTemplate = "" + 
"<div class=\"list-group-item todo container\" data-todo-priority=\"<%= todo.priority %>\" data-todo-order=\"<%= todo.order %>\" data-todo-id=\"<%= todo.id %>\">" +
"    <div class=\"glyphicon glyphicon-sort sort icon pull-left\"></div>" +
"    <div class=\"priority pull-left btn\"><%= todo.priority %></div>" +
"    <div class=\"content pull-left\"><%= todo.content %></div>" +
"    <button class=\"delete btn btn-danger pull-right\">Delete</button>" +
"</div>";
var compiledTodoTemplate = _.template(todoTemplate);

function showSortIcons() {
    $(".stack:not(.trash) .todo .sort.icon").each(function (index, elem) {
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
    $(".stack:not(.trash) .todo .delete.btn:not(.control)").each(function (index, elem) {
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

function getCookie(c_name)
{
    var c_value = document.cookie;
    var c_start = c_value.indexOf(" " + c_name + "=");
    if (c_start == -1) {
        c_start = c_value.indexOf(c_name + "=");
    }
    if (c_start == -1) {
        c_value = null;
    } else {
        c_start = c_value.indexOf("=", c_start) + 1;
        var c_end = c_value.indexOf(";", c_start);
        if (c_end == -1) {
            c_end = c_value.length;
        }
        c_value = unescape(c_value.substring(c_start,c_end));
    }
    return c_value;
}
function handleCommands(commandsTimePair) {
    for(var i = 0; i < commandsTimePair.length; i++) {
        var command = commandsTimePair[i];
        if (command.command === "push") {
            var stack = $(".stack:not(.trash)");
            var domStr = compiledTodoTemplate({todo: command.data});
            stack.prepend(domStr);
            $("#control-todo-content").val("");
            if ($(".delete.btn:not(.control):last").css("display") !== "display") {
                hideDeleteButtons();
            }
            if ($(".sort.icon:last").css("display") !== "display") {
                hideSortIcons();
            }
            bindUIEventHandlerToTodoView();

        } else if (command.command === "update") {
            console.log(command);
            var todoDom = $(".stack .todo[data-todo-id=" + command.data.id + "]");
            todoDom.attr("data-todo-order", command.data.order);
            todoDom.attr("data-todo-priority", command.data.priority);
            todoDom.children(".priority").html(command.data.priority);
        } else if (command.command === "removeItem") {
            $(".stack .todo[data-todo-id=" + command.data.id + "]").remove();
        } else if (command.command === "pop") {
            var todo = $(".stack:not(.trash) .todo:first");
            todo.select(".delete").remove();
            todo.select(".sort").remove();
            todo.select(".priority").remove();
            $(".trash.stack").append(todo);
            if ($(".trash.stack .todo:first").css("display") === "none") {
                hideItemsInTrashStackExceptLastNItems(2);
            }
        }
    }
    $(".stack:not(.trash) .todo").sort(function (a,b) {
        console.log(a, b);
        return $(a).attr("data-todo-order") < $(b).attr("data-todo-order") ? 1 : -1;
    }).appendTo(".stack:not(.trash)");
}

function hideItemsInTrashStackExceptLastNItems(num) {
    num = Math.max(0, ($(".trash.stack .todo").length - num + 1));
    target = $(".trash.stack .todo:not(:nth-child(n+"+ num +"))");
    target.each(function (index, elem) {
        if ($(elem).css("display") === "block") {
            $(elem).animate({"height": "toggle"});
        }
    });
    $("#trash_expand_collapse_btn").html("Expand");
}

function showItemsInTrashStackExceptLastNItems(num) {
    num = Math.max(0, ($(".trash.stack .todo").length - num + 1));
    target = $(".trash.stack .todo:not(:nth-child(n+"+ num +"))");
    target.each(function (index, elem) {
        if ($(elem).css("display") === "none") {
            $(elem).animate({"height": "toggle"});
        }
    });
    $("#trash_expand_collapse_btn").html("Collapse");
}

function initControls() {
    $(".control.pop").click(function() {
        $.ajax({ url: "/stack/" + window.stackName + "/pop/" });
    });
    $(".control.push").click(function() {
        $.ajax({
            url: "/stack/" + window.stackName + "/push/" , type:"POST",
            data:{"item":$("#control-todo-content").val()}
        });
    });
    $(".control.delete").click(function() {
        if ($(".delete.btn:not(.control):last").css("display") === "none") {
            showDeleteButtons();
        } else {
            hideDeleteButtons();
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
            $.ajax({ url: "/stack/" + window.stackName + "/moveItem/" + from + "/" + to + "/" });
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
        $.ajax({url: "/stack/" + window.stackName + "/raisePriority/" + index + "/" }).done(function (){
            $(e.target).html((parseInt($(e.target).html()) + 1) % 5);
        });
    });

    $(".stack:not(.trash) .todo .delete").unbind().click(function (e){
        $.ajax({url: "/stack/" + window.stackName + "/removeItem/" + $(e.target).parent().index() + "/"})
    });
}
(function() {
    setSequenceNumber(getCookie("sequenceNumber") || 0);
    initControls();
    bindUIEventHandlerToTodoView();
    hideItemsInTrashStackExceptLastNItems(2);
    hideSortIcons();
    hideDeleteButtons();

    var handleFetchResponse = function (data) {
        data = JSON.parse(data);
        setSequenceNumber(parseInt(data.command_update_sequence_number));
        for (var i = 0; i < data.commands.length; i++) {
            if (data.commands[i] !== null) {
                var commands = data.commands[i].commands;
                if (commands !== undefined) {
                    handleCommands(commands);
                }
            }
        }
    }
    function poll () {
        $.ajax({url: "/stack/" + window.stackName + "/fetch/" + getSequenceNumber() + "/"}).done(function (data) {
            handleFetchResponse(data);
            poll();
        });
    }
    poll();
})();
