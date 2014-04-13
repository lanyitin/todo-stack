function initControls() {
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

angular.module("Stacktodos", ["ng"], function($interpolateProvider) {
    $interpolateProvider.startSymbol('{[');
        $interpolateProvider.endSymbol(']}');
})
.controller("AppController", function ($scope, $http, $filter) {
    $scope.stack = [];
    $scope.trash_stack = [];
    $scope.expandTrashStack = false;

    function refreshUI() {
        $scope.$apply();
    }

    $scope.getExpandTrashText = function () {
        if ($scope.expandTrashStack) {
            return "Collapse";
        } else {
            return "Expand";
        }
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

    $scope.toggleExpandTrash = function () {
        $scope.expandTrashStack ^= true;
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

    $scope.pop = function (id) {
        target = $filter('orderBy')($scope.stack, "order", true);
        if (target.length) {
            target = target[0];
            $http.get("/moveToTrash/" + target.id)
            .success(function (data) {
                angular.forEach(data, function (todo) {
                    console.log(todo);
                    console.log(getIndexById(todo.id, 1));
                    $scope.trash_stack.push($scope.stack.splice(getIndexById(todo.id, 1))[0]);
                });
            });
        }
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

    $scope.clean_trash = function () {
        $http.get("/clean_trash/")
            .success(function (data) {
            angular.forEach($scope.trash_stack, function(existTodo, idx) {
                angular.forEach(data, function(target) {
                    if (existTodo.id == target.id) {
                        $scope.trash_stack.splice(idx, 1);
                    }
                });
            });
        });
    }
})
.filter('reverse', function() {
    return function(items) {
        return items.slice().reverse();
    };
})
.filter('expand', function() {
    return function(items, expandTrashStack) {
        if (expandTrashStack) {
            return items;
        } else {
            return items.slice(items.length - 2);
        }
    };
});
