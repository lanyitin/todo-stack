var sequenceNumber;

function getSequenceNumber() {
    return sequenceNumber;
}
function setSequenceNumber(n) {
    sequenceNumber = n;
}
var compiledTodoTemplate = _.template($("#todo_template").html());

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
    $(".stack:not(.trash) .todo .delete").each(function (index, elem) {
        if ($(elem).css("display") === "none") {
            $(elem).toggle();
        }
    });
}
function hideDeleteButtons() {
    $(".stack:not(.trash) .todo .delete").each(function (index, elem) {
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
        console.log(command);
        if (command.command == "push") {
            var stack = $(".stack:not(.trash)");
            var domStr = compiledTodoTemplate({todo: command.data});
            stack.prepend(domStr);
            $("#control-todo-content").val("");
        } else if (command.command == "append") {
            var stack = $(".stack:not(.trash)");
            var domStr = compiledTodoTemplate({todo: command.data});
            stack.append(domStr);
            $("#control-todo-content").val("");
        } else if (command.command == "append_trash") {
            var stack = $(".stack.trash");
            var domStr = compiledTodoTemplate({todo: command.data});
            stack.append(domStr);
        } else if (command.command == "update") {
            var todoDom = $(".stack .todo[data-todo-id=" + command.data.id + "]");
            todoDom.attr("data-todo-order", command.data.order);
            todoDom.attr("data-todo-priority", command.data.priority);
            todoDom.children(".priority").html(command.data.priority);
        } else if (command.command == "removeItem") {
            $(".stack .todo[data-todo-id=" + command.data.id + "]").remove();
        } else if (command.command == "pop") {
            var todo = $(".stack:not(.trash) .todo:first");
            $(".trash.stack").append(todo);
        }
    }
    $(".stack:not(.trash) .todo").sort(function (a,b) {
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
        $.ajax({ url: "/pop/" });
    });
    $(".control.push").click(function() {
        $.ajax({
            url: "/push/" , type:"POST",
            data:{"item":$("#control-todo-content").val()}
        });
    });
    $(".control.append").click(function() {
        $.ajax({
            url: "/append/" , type:"POST",
            data:{"item":$("#control-todo-content").val()}
        });
    });
    $(".control.clean.trash").click(function() {
        $.ajax({
            url: "/clean_trash"
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
    var toggleTrashStack = function (e, thiz) {
        if ($(".trash.stack .todo:first").css("display") === "block") {
            hideItemsInTrashStackExceptLastNItems(2);
        } else {
            showItemsInTrashStackExceptLastNItems(2);
        }
    }
    $("#trash_expand_collapse_btn").click(toggleTrashStack);
    $(".sortable").sortable({
        start: function ( event, ui ) {
            ui.item.data("start_pos", ui.item.index());
        },
        update: function ( event, ui) {
            var from = ui.item.data("start_pos");
            var to = ui.item.index();
            $.ajax({ url: "/moveItem/" + from + "/" + to + "/" });
        },
        revert: true,
        handle: ".sort.icon"
    });
}

function bindUIEventHandlerToTodoView() {
    $(document).on('click', ".todo .priority", function(e) {
        var todoId = $(e.target).parent().attr("data-todo-id");
        $.ajax({url: "/raisePriority/" + todoId + "/" }).done(function (){
            $(e.target).html((parseInt($(e.target).html()) + 1) % 5);
        });
    });

    $(document).on('click', ".stack:not(.trash) .todo .delete", function (e){
        $.ajax({url: "/removeItem/" + $(e.target).parent().attr("data-todo-id") + "/"})
    });

    $(document).on('change', ".stack:not(.trash)", function () {
        if ($(".stack:not(.trash) .todo:last .delete").css("display") === "block") {
            showDeleteButtons();
        } else {
            hideDeleteButtons();
        }

        if ($(".stack:not(.trash) .todo:last .sort").css("display") === "block") {
            showSortIcons();
        } else {
            hideSortIcons();
        }
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
        $.ajax({url: "/fetch/" + getSequenceNumber() + "/"}).done(function (data) {
            handleFetchResponse(data);
            poll();
        });
    }
    poll();
})();
