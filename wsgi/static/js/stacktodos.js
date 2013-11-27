var todoTemplate = "<div class=\"list-group-item todo container\" data-todo-priority=\"<%= todo.priority %>\" data-todo-order=\"<%= todo.order %>\" data-todo-id=\"<%= todo.id %>\"> <div class=\"col-md-1 glyphicon glyphicon-sort sort icon\"></div> <div class=\"col-md-10 content\"><%= todo.content %></div> <button class=\"delete btn btn-danger pull-right col-md-2\">Delete</button> </div>"
var compiledTodoTemplate = _.template(todoTemplate);
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
            } else if (command.command === "update") {
                var todoDom = $(".stack .todo[data-todo-id=" + command.data.id + "]");
                console.log(todoDom);
                todoDom.attr("data-todo-order", command.data.order);
                todoDom.attr("data-todo-priority", command.data.priority);
            } else if (command.command === "delete") {
                $(".stack .todo[data-todo-id=" + command.data.id + "]").remove();
            } else if (command.command === "pop") {
                $(".trash.stack").append($(".stack:not(.trash) .todo:first"))
            }
        }
    }
}
(function() {

    $(".control.pop").click(function() {
        $.ajax({url: "/" + window.stackName + "/pop"}).done(function (response) {handleResponse(response);});
    });
    $(".control.push").click(function() {
        $.ajax({url: "/" + window.stackName + "/push", type:"POST", data:{"item":$("#control-todo-content").val()}}).done(function (response) {handleResponse(response);});
    });
    $(".sortable").sortable({
        start: function ( event, ui ) {
            ui.item.data("start_pos", ui.item.index());
        },
        update: function ( event, ui) {
            var from = ui.item.data("start_pos");
            var to = ui.item.index();
            $.ajax({url: "/" + window.stackName + "/moveItem/" + from + "/" + to}).done(function (response) {handleResponse(response)});
        },
        revert: true,
        handle: ".sort.icon"
    });

    $(".delete.control").click(function() {
        $(".delete.btn:not(.control)").toggle();
    })
    $(".delete.btn:not(.control)").toggle();

    $(".sort.icon").toggle();
    $(".sort.control").click(function() {
        $(".sort.icon").toggle();
    });
    $("#trash_expand_collapse_btn").click(function (e, thiz) {
        target = $(".trash.stack .todo:not(:nth-child(n+"+($(".trash.stack .todo").length - 1) +"))");
        target.animate({height:"toggle"}, function () {
            if (target.css("display") === "none") {
                $(e.target).html("Expand");
            } else {
                $(e.target).html("Collapse");
            }
        });
    });
    $("#trash_expand_collapse_btn").click();
    $(".todo .priority").click(function(e) {
        var currentPriority = $(e.target).attr("data-todo-priority");
        var todoId = $(e.target).attr("data-todo-id");
        var index = $(e.target).parent().index();
        $.ajax({url: "/" + window.stackName + "/raisePriority/" + index}).done(function (){
            $(e.target).html((parseInt($(e.target).html()) + 1) % 5);
        });
    });
    $(".stack:not(.trash) .todo").select(".delete").unbind().click(function (e){
        $.ajax({url: "/" + window.stackName + "/removeItem/" + $(e.target).parent().index()}).done(function () {
            console.log($(e.target).parent().remove());
        });
        
    });
})();
