function CoreController($scope, $http, $filter, $sce, $log) {
    $scope.stack = [];
    $scope.trash_stack = [];
    $scope.expandTrashStack = false;

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


    $scope.$on('update', function (event, todo) {
        handleItem(todo);
    });
    function handleItem(item) {
        if (getTodoById(item.id) == undefined) {
            $scope.stack.push(item);
        } else {
            $scope.stack[getIndexById(item.id)] = item
        }
    }

    function newItem(action, todo) {
        if (todo === undefined) {
            if ($scope.new_todo_content != "") {
                $http.post(action, {item: $scope.new_todo_content}).success(function (data, status) {
                    if (status == 200) {
                        $scope.new_todo_content = "";
                        angular.forEach(data, function(item) {
                            $scope.$emit('update', item);
                        });
                    }
                });
            }
        } else {
            handleItem(todo);
        }
    }

    $scope.push = function (todo) {
        if (todo === undefined) {
            order_list = $scope.stack.map(function (todo) {
                return todo.order;
            });
            $log.log(order_list);
            todo = {content:$scope.new_todo_content, priority:2, tags:[], id:undefined, order:(Math.max.apply(-1, order_list) + 1)}
            todo.id = Date.now();
            if (todo.order === -Infinity) {
                todo.order = 0;
            }
            $scope.new_todo_content = "";
        }
        $scope.$emit("update", todo);
    }

    $scope.append = function (todo) {
        if (todo === undefined) {
            todo = {content:$scope.new_todo_content, priority:2, tags:[], id:undefined, order:0}
            todo.id = Date.now();
            $scope.new_todo_content = "";
        }
        angular.forEach($scope.stack, function(item) {
            item.order += 1;
            $scope.$emit('update', item);
        });
        $scope.$emit("update", todo);
    }

    $scope.$on("removeItem", function (event, target_todo) {
        var tmp_stack = [];
        angular.forEach($scope.stack, function (todo) {
            tmp_stack.push(todo);
        });
        angular.forEach($scope.stack, function (todo, idx) {
            if (todo.id == target_todo.id) {
                delete tmp_stack[idx];
            }
        });
        $log.log(tmp_stack);
        $scope.stack = $.grep(tmp_stack, function (item) {return item != undefined})
    });
    $scope.removeTodo = function (id) {
        var todo = getTodoById(id);
        $scope.$emit("removeItem", todo);
    }

    $scope.$on('pop', function (event) {
        tmp_stack = [];
        angular.forEach($filter('orderBy')($scope.stack, "order", true), function (todo) {
            tmp_stack.push(todo);
        });
        if (tmp_stack.length > 0) {
            target = tmp_stack[0];
            delete tmp_stack[0];
            $scope.stack = $.grep(tmp_stack, function (item) {return item != undefined})
            $scope.trash_stack.push(target);
        }
    });
    $scope.pop = function () {
        $scope.$emit('pop');
    }


    $scope.moveTodo = function (todo) {
        handleItem(todo);
    }


    $scope.raisePriority = function (id) {
        var todo = getTodoById(id);
        todo.priority  = (todo.priority + 1) % 5;
        $scope.$emit('update', todo);
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

    $scope.$on('cleanTrash', function (event) {
        $scope.trash_stack = [];
    });
    $scope.clean_trash = function () {
        $scope.$emit('cleanTrash');
    }


    $scope.toggleExpandTrash = function () {
        $scope.expandTrashStack ^= true;
    }


    $scope.marked = function (str) {
        return $sce.trustAsHtml(marked(str));
    }
}

function AppController($scope, $http, $filter, $sce, $log) {
    CoreController.call(this, $scope, $http, $filter, $sce, $log);
    $scope.raisePriority = function (id) {
        $http.get("/raisePriority/" + id + "/")
            .success(function (data, status){
                if (status == 200) {
                    angular.forEach(data, function(item) {
                        if (item.id = id) {
                            $scope.$emit('update', id);
                        }
                    });
                }
            });
    }


    $scope.push = function (todo) {
        if (todo === undefined) {
            $http.post("/push/", {item: $scope.new_todo_content}).success(function (data, status) {
                if (status == 200) {
                    $scope.new_todo_content = "";
                    angular.forEach(data, function(item) {
                        $scope.$emit("update", item);
                    });
                }
            });
        } else {
            $scope.$emit("update", todo);
        }
    }


    $scope.append = function (todo) {
        if (todo === undefined) {
            $http.post("/append/", {item: $scope.new_todo_content}).success(function (data, status) {
                if (status == 200) {
                    $scope.new_todo_content = "";
                    angular.forEach(data, function(item) {
                        $scope.$emit("update", item);
                    });
                }
            });
        } else {
            $scope.$emit("update", todo);
        }
    }


    $scope.removeTodo = function (id) {
        $http.get("/removeItem/" + id + "/")
            .success(function (data, status) {
                if (status == 200) {
                    $scope.$emit("removeItem", data[0]);
                }
            });
    }


    $scope.pop = function () {
        target = $filter('orderBy')($scope.stack, "order", true);
        if (target.length) {
            target = target[0];
            $http.get("/moveToTrash/" + target.id + "/")
                .success(function (data, status) {
                    if (status == 200 && data[0].id == target.id) {
                        $scope.$emit('pop');
                    }
                });
        }
    }


    $scope.clean_trash = function () {
        $http.get("/clean_trash/")
            .success(function (data, status) {
                if (status == 200) {
                    var tmp_trash = [];
                    angular.forEach($scope.trash_stack, function(existTodo, idx) {
                        tmp_trash.push(existTodo);
                    });
                    angular.forEach(tmp_trash, function(existTodo, idx) {
                        angular.forEach(data, function(target) {
                            if (existTodo.id == target.id) {
                                delete tmp_trash[idx];
                            }
                        });
                    });
                    $scope.trash_stack = $.grep(tmp_trash, function (item) {return item != undefined});
                }
            });
    }

}
AppController.prototype = Object.create(CoreController.prototype)


angular.module("Stacktodos", ["ng", "ui.sortable"], function($interpolateProvider) {
    $interpolateProvider.startSymbol('{[');
        $interpolateProvider.endSymbol(']}');
})
.controller("Tomatoes", function($scope, $interval) {
    var breakSound = new Audio("static/sound/doorbell-1.mp3");
    var workSound = new Audio("static/sound/doorbell-2.mp3");
    function Countdown(num) {
        this.number = num;
        this.tick = function () {
            this.number -= 1;
        }
    }

    function TomatoesClock(noSound) {
        if (!noSound) {
            workSound.play();
        }
        this.counter = new Countdown(25 * 60);
        this.tick = function () {
            this.counter.tick()
            if  (this.counter.number > 0) {
                return this;
            } else {
                return new BreakClock();
            }
        }
    }

    function BreakClock(noSound) {
        if (!noSound) {
            breakSound.play();
        }
        this.counter = new Countdown(5 * 60);
        this.tick = function () {
            this.counter.tick()
            if  (this.counter.number > 0) {
                return this;
            } else {
                return new TomatoesClock();
            }
        }
    }

    function NullClock() {
        this.counter = new Countdown(25 * 60);
        this.tick = function () {
            return this;
        }
    }

    $scope.get_remain_time = function() {
        var number = $scope.clock.counter.number;
        
        var min_str = Math.floor(number / 60);
        if (min_str < 10) {
            min_str = "0" + min_str.toString();
        }

        var sec_str = number % 60;
        if (sec_str < 10) {
            sec_str = "0" + sec_str.toString();
        }
        return min_str + ":" + sec_str;
    }

    $scope.get_trigger_text = function () {
        if ($scope.clock instanceof NullClock) {
            return "Start";
        } else {
            return "Stop";
        }
    }

    $scope.get_trigger_style = function () {
        if ($scope.clock instanceof NullClock) {
            return "btn-default";
        } else {
            return "btn-danger";
        }
    }

    $scope.trigger = function () {
        if ($scope.clock instanceof NullClock) {
            $scope.clock = new TomatoesClock(true);
        } else {
            $scope.clock = new NullClock();
        }
    }

    $scope.clock = new NullClock();
    $interval(function () {
        $scope.clock = $scope.clock.tick();
    }, 1000);
})
.controller("AppController", AppController)
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

$(document).on("keyup", function(ev) {
    if (ev.keyCode == 27) {
        $("#control-todo-content").blur();
        return;
    }
});

$(document).on("keypress", function(ev) {
    if (ev.charCode != 13 && !$("#control-todo-content").is(":focus")) {
        $("#control-todo-content").focus();
    }
});

$(function() {
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
                angular.forEach(data, function (todo) {
                    angular.element("[ng-controller=AppController").scope().moveTodo(todo);
                });
            });
        },
        revert: true,
        handle: ".sort.icon",
        axis: "y"
    });

});
