function CoreController($scope, $http, $filter, $sce, $log) {
    $scope.stack = [];
    $scope.expandTrashStack = false;
    $scope.input_priority = 2;
    $scope.input_required_clock = 1;

    $scope.getExpandTrashText = function () {
        if ($scope.expandTrashStack) {
            return "Collapse";
        } else {
            return "Expand";
        }
    }

    $scope.update_input_priority = function () {
        $scope.input_priority = ($scope.input_priority + 1) % 5;
    }

    $scope.update_input_required_clock = function () {
        $scope.input_required_clock = ($scope.input_required_clock) % 3 + 1;
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


    $scope.$on('update', function (event, todo, notAlarm) {
        handleItem(todo, notAlarm);
    });
    function handleItem(item, notAlarm) {
        if (getTodoById(item.id) == undefined) {
            $scope.stack.push(item);
        } else {
            $scope.stack[getIndexById(item.id)] = item
        }

        var top_todo = $filter('is_in_trash')($filter('orderBy')($scope.stack, "order", true), false);
        if (top_todo.length === 0) {
            return;
        }
        top_todo = top_todo[0];
        if (top_todo.required_clock + top_todo.extended_clock - top_todo.consumed_clock > 0) {
            return;
        }
        if (notAlarm) {
            $scope.pop();
        } else {
            $("#todoManipulateModal").modal({
                show: true,
                backdrop: 'static'
            });
        }
    }


    $scope.push = function (todo) {
        if (todo === undefined) {
            order_list = $scope.stack.map(function (todo) {
                return todo.order;
            });
            todo = {content:$scope.new_todo_content, priority:2, tags:[], id:undefined, order:(Math.max.apply(-1, order_list) + 1), in_trash: false}
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
            todo = {content:$scope.new_todo_content, priority:2, tags:[], id:undefined, order:0, in_trash: false}
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
        $scope.stack = $.grep(tmp_stack, function (item) {return item != undefined})
    });
    $scope.removeTodo = function (id) {
        var todo = getTodoById(id);
        $scope.$emit("removeItem", todo);
    }

    $scope.$on('pop', function (event, target) {
        tmp_stack = [];
        if (target == undefined) {
            angular.forEach($filter('is_in_trash')($filter('orderBy')($scope.stack, "order", true), false), function (todo) {
                tmp_stack.push(todo);
            });
            if (tmp_stack.length > 0) {
                target = tmp_stack[0];
                target.in_trash = true;
            }
        } else {
            angular.forEach($scope.stack, function (todo) {
                if (todo.id == target.id) {
                    todo.in_trash = target.in_trash;
                    todo.order = target.order;
                }
            });
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

    $scope.content_keypress = function (event) {
        if (event.keyCode == 13) {
            if (event.shiftKey) {
                $scope.push();
            } else {
                $scope.append();
            }
        }
    }

    $scope.$on('cleanTrash', function (event) {
        var tmp_stack = [];
        angular.forEach($scope.stack, function(existTodo, idx) {
            tmp_stack.push(existTodo);
        });
        angular.forEach(tmp_stack, function(existTodo, idx) {
            if (existTodo.in_trash == true) {
                delete tmp_stack[idx];
            }
        });
        $scope.stack = $.grep(tmp_stack, function (item) {return item != undefined});
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

function DemoController($scope, $http, $filter, $sce, $log, $interval, $timeout) {
    CoreController.call(this, $scope, $http, $filter, $sce, $log);

    function typeText(txt, callback) {
        var txtLen = txt.length;
        var char = 0;
        $scope.new_todo_content = "|";
        var humanize = Math.round(Math.random() * 200 - 30) + 30;
        var timeOut = $interval(function() {
            char++;
            var type = txt.substring(0, char);
            $scope.new_todo_content = type + '|';

            if (char == txtLen) {
                $scope.new_todo_content = $scope.new_todo_content.slice(0, -1); // remove the '|'
                $scope.append();
                $interval.cancel(timeOut);
                callback();
            }
        }, humanize);
    }

    typeText("visist [todo-stack](http://todos.lanyitin.tw)", function() {
        $timeout(function () {
            $scope.pop();
            typeText("create an account", function () {
                typeText("bookmark this page", function () {});
            });
        }, 200);
    });
}

function AppController($scope, $rootScope, $http, $filter, $sce, $log) {
    CoreController.call(this, $scope, $http, $filter, $sce, $log);


    $scope.raisePriority = function (id) {
        $http.get("/raisePriority/" + id + "/")
            .success(function (data, status){
                if (status == 200) {
                    angular.forEach(data, function(item) {
                        if (item.id = id) {
                            $scope.$emit('update', item);
                        }
                    });
                }
            });
    }

    $rootScope.$on("TomatoeConsumed", function (evt) {
        target = $filter('is_in_trash')($filter('orderBy')($scope.stack, "order", true), false);
        if (target.length) {
            target = target[0];
            $http.get("/consume/" + target.id + "/")
                .success(function (data, status){
                    if (status == 200) {
                        angular.forEach(data, function(item) {
                            $scope.$emit('update', item, false);
                        });
                    }
                });
        }
    });


    $scope.push = function (todo) {
        if (todo === undefined) {
            if ($scope.new_todo_content.trim() == "") {
                return;
            }
            var tmp_content = $scope.new_todo_content;
            $scope.new_todo_content = "";
            var parameters = {"item": tmp_content, "priority": $scope.input_priority, "required_clock": $scope.input_required_clock};
            $http.post("/push/", parameters).success(function (data, status) {
                if (status == 200) {
                    angular.forEach(data, function(item) {
                        $scope.$emit("update", item);
                    });
                } else {
                    $scope.new_todo_content = tmp_content;
                }
            });
        } else {
            $scope.$emit("update", todo);
        }
    }


    $scope.append = function (todo) {
        if (todo === undefined) {
            if ($scope.new_todo_content.trim() == "") {
                return;
            }
            var tmp_content = $scope.new_todo_content;
            $scope.new_todo_content = "";
            var parameters = {"item": tmp_content, "priority": $scope.input_priority, "required_clock": $scope.input_required_clock};
            $http.post("/append/", parameters).success(function (data, status) {
                if (status == 200) {
                    $scope.new_todo_content = "";
                    angular.forEach(data, function(item) {
                        $scope.$emit("update", item);
                    });
                } else {
                    $scope.new_todo_content = tmp_content;
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
        target = $filter('is_in_trash')($filter('orderBy')($scope.stack, "order", true), false);
        if (target.length) {
            target = target[0];
            target.in_trash = true;
            $http.get("/moveToTrash/" + target.id + "/")
                .success(function (data, status) {
                    data = data[0];
                    if (status == 200 && data.id == target.id) {
                        target.order = data.order;
                        $scope.$emit('pop', data);
                    }
                });
        }
    }


    $scope.clean_trash = function () {
        $http.get("/clean_trash/")
            .success(function (data, status) {
                if (status == 200) {
                    $scope.$emit("cleanTrash");
                }
            });
    }

    $scope.content_keypress = function (event) {
        if (event.keyCode == 13) {
            if (event.shiftKey) {
                $scope.push();
            } else {
                $scope.append();
            }
        }
    }

    $scope.addClock = function (event) {
        target = $filter('is_in_trash')($filter('orderBy')($scope.stack, "order", true), false);
        if (target.length) {
            target = target[0];
            target.in_trash = true;
            $http.get("/add_extended_clock/" + target.id + "/" + 1 + "/")
                .success(function (data, status) {
                    data = data[0];
                    if (status == 200 && data.id == target.id) {
                        target.order = data.order;
                        $scope.$emit('update', data);
                    }
                });
        }
    }

}
AppController.prototype = Object.create(CoreController.prototype);
DemoController.prototype = Object.create(CoreController.prototype);


angular.module("Stacktodos", ["ng", "ui.sortable"], function($interpolateProvider) {
    $interpolateProvider.startSymbol('{[');
        $interpolateProvider.endSymbol(']}');
})
.controller("Tomatoes", function($scope, $rootScope, $interval) {
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
                $rootScope.$emit("TomatoeConsumed");
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
})
.filter('is_in_trash', function () {
    return function (items, in_trash) {
        ary = [];
        angular.forEach(items, function (todo) {
            if (todo.in_trash == in_trash) {
                ary.push(todo);
            }
        });
        return ary;
    }
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
            var from = Math.abs(ui.item.data("start_pos") - ($(".stack:not(.trash) .todo").size() - 1));
            var to = Math.abs(ui.item.index() - ($(".stack:not(.trash) .todo").size() - 1));
            $.ajax({ 
                url: "/moveItem/" + from + "/" + to + "/"
            }).done(function (data) {
                angular.forEach(data, function (todo) {
                    angular.element("[ng-controller=AppController]").scope().moveTodo(todo);
                });
            });
        },
        revert: true,
        handle: ".sort.icon",
        axis: "y"
    });

});
