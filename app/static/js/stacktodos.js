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


function initControls() {
    $(".control.pop").click(function() {
        $.ajax({ 
            url: "/moveToTrash/" + $(".stack:not(.trash) .todo:first").attr("data-todo-id")
        }).done(function (data) {
            handleCommands(JSON.parse(data).commands);
        });
    });
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
                $("#control-todo-content").val("");
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

    $scope.removeTodo = function (id) {
        $http.get("/removeItem/" + id + "/")
        .success(function (data) {
            angular.forEach(data, function (todo) {
                var target = getIndexById(todo.id);
                if (target != undefined) {
                    $scope.stack.splice(target, 1);
                } else {
                    console.log($scope.stack);
                    console.log(id, todo, todo.id, getIndexById(id));
                }
            });
        });
    }

    $scope.moveTodo = function () {

    }

    $scope.raisePriority = function (id) {
        $http.get("/raisePriority/" + id + "/")
        .success(function (data){
            angular.forEach(data, function(item) {
                handleItem(item);
            });
        });
    }

    $scope.content_keypress = function ($event) {
        if ($event.charCode == 13) {
            if ($event.shiftKey) {
                $scope.push();
            } else {
                $scope.append();
            }
        }
    }
})
.filter('reverse', function() {
    return function(items) {
        return items.slice().reverse();
    };
});
