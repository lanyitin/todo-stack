var sequenceNumber;

function getSequenceNumber() {
    return sequenceNumber;
}
function setSequenceNumber(n) {
    sequenceNumber = n;
}
var compiledTodoTemplate;
if ($("#todo_template").size() > 0) {
    compiledTodoTemplate = _.template($("#todo_template").html());
}

function hideItemsInTrashStackExceptLastNItems(num) {
    num = Math.max(0, ($(".trash.stack .todo").length - num + 1));
    target = $(".trash.stack .todo:not(:nth-child(n+"+ num +"))");
    target.hide();
    $("#trash_expand_collapse_btn").html("Expand Trash");
}

function showItemsInTrashStackExceptLastNItems(num) {
    num = Math.max(0, ($(".trash.stack .todo").length - num + 1));
    target = $(".trash.stack .todo:not(:nth-child(n+"+ num +"))");
    target.show();
    $("#trash_expand_collapse_btn").html("Collapse Trash");
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


function initControls() {
    $(".control.pop").click(function() {
        $.ajax({ 
            url: "/moveToTrash/" + $(".stack:not(.trash) .todo:first").attr("data-todo-id")
        }).done(function (data) {
            handleCommands(JSON.parse(data).commands);
        });
    });
    // $(".control.push").click(function() {
    //     $.ajax({
    //         url: "/push/" , type:"POST",
    //         data:{"item":$("#control-todo-content").val()}
    //     }).done(function (data) {
    //         console.log(data);
    //         handleCommands(JSON.parse(data).commands);
    //     });
    // });
    // $(".control.append").click(function() {
    //     $.ajax({
    //         url: "/append/" , type:"POST",
    //         data:{"item":$("#control-todo-content").val()}
    //     }).done(function (data) {
    //         handleCommands(JSON.parse(data).commands);
    //     });
    // });
    $(".control.clean.trash").click(function() {
        $.ajax({
            url: "/clean_trash"
        }).done(function (data) {
            handleCommands(JSON.parse(data).commands);
        });
    });
    var toggleTrashStack = function (e, thiz) {
        if ($(".trash.stack .todo:first").is(":hidden")) {
            showItemsInTrashStackExceptLastNItems(2);
        } else {
            hideItemsInTrashStackExceptLastNItems(2);
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
            $.ajax({ 
                url: "/moveItem/" + from + "/" + to + "/"
            }).done(function (data) {
                handleCommands(JSON.parse(data).commands);
            });
        },
        revert: true,
        handle: ".sort.icon",
        axis: "y"
    });
}

$(document).on('click', ".todo .priority", function(e) {
    var todoId = $(e.target).parent().attr("data-todo-id");
    $.ajax({url: "/raisePriority/" + todoId + "/" }).done(function (data){
        $(e.target).html((parseInt($(e.target).html()) + 1) % 5);
        handleCommands(JSON.parse(data).commands);
    });
});

$(document).on('click', ".todo .delete", function (e){
    $.ajax({
        url: "/removeItem/" + $(e.target).parent().parent().attr("data-todo-id") + "/"
    }).done(function (data) {
        handleCommands(JSON.parse(data).commands);
    });
});

$(".stack").on('DOMNodeInserted DOMNodeRemoved', function () {
    if ($(".stack.trash .todo:first").is(":hidden")) {
        hideItemsInTrashStackExceptLastNItems(2);
    } else {
        showItemsInTrashStackExceptLastNItems(2);
    }
});
$(document).ready(function () {
    setSequenceNumber(getCookie("sequenceNumber") || 0);
    initControls();
    hideItemsInTrashStackExceptLastNItems(2);
});


angular.module("Stacktodos", ["ng"], function($interpolateProvider) {
    $interpolateProvider.startSymbol('{[');
        $interpolateProvider.endSymbol(']}');
})
.controller("AppController", function ($scope, $http) {
    $scope.stack = [];
    $scope.trash_stack = [];
    $scope.sync = function () {

    }
    function getTodoById(id) {
        var target = undefined;
        angular.forEach($scope.stack, function(item) {
            console.log(item.id == id, item.id, id);
            if (item.id == id) {
                target = item;
            }
        });
        return target;
    }

    function getIndexById(id) {
        var target = undefined;
        angular.forEach($scope.stack, function(item, idx) {
            if (item.id == id) {
                target = idx;
            }
        });
        return target;
    }

    function handleItem(item) {
        if (getTodoById(item.id) == undefined) {
            $scope.stack.push(item);
        } else {
            $scope.stack[getIndexById(item.id)] = item
        }
    }

    function newItem(action, todo) {
        if (todo === undefined) {
            content = $("#control-todo-content").val();
            $http.post(action, {item: content}).success(function (data) {
                angular.forEach(data, function(item) {
                    handleItem(item);
                });
            });
        } else {
            handleItem(todo);
        }
    }

    $scope.push = function (todo) {
        newItem("/push/", todo);
    }

    $scope.append = function (todo) {
        newItem("/append/", todo);
    }

    $scope.removeTodo = function () {

    }

    $scope.moveTodo = function () {

    }

    $scope.raisePriority = function () {

    }
})
.filter('reverse', function() {
    return function(items) {
        return items.slice().reverse();
    };
});
