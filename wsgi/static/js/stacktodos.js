(function() {
    $(".sortable").sortable({
        start: function ( event, ui ) {
            ui.item.data("start_pos", ui.item.index());
        },
    update: function ( event, ui) {
        var from = ui.item.data("start_pos");
        var to = ui.item.index();
        console.log("from", from , "to", to);
        $.ajax({url: "/{{ stack.name }}/moveItem/" + from + "/" + to}).done(function (response) {console.log(response)});
    },
    revert: true,
    handle: ".sort.icon"
    });
    $(".stack:not(.trash) .todo").each(function(index, elem){
        $(elem).append($("<a/>").addClass("delete btn btn-danger pull-right col-md-2").attr("href", "/{{ stack.name }}/removeItem/" + index).html("Delete"))
        $(elem).prepend($("<div/>").addClass("col-md-1 glyphicon glyphicon-sort sort icon"));
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
        $(".stack.trash .todo:not(:nth-child(n+2))").animate({height:"toggle"}, function () {
            if ($(".stack.trash .todo:not(:nth-child(n+2))").css("display") === "none") {
                $(e.target).html("Expand");
            } else {
                $(e.target).html("Collapse");
            }
        });
    });
    $("#trash_expand_collapse_btn").click();
    $(".priority").click(function(e) {
        var currentPriority = $(e.target).attr("data-todo-priority");
        var todoId = $(e.target).attr("data-todo-id");
        var index = $(e.target).parent().index();
        $.ajax({url: "/{{ stack.name }}/raisePriority/" + index}).done(function (){
            $(e.target).html((parseInt($(e.target).html()) + 1) % 5);
        });
    });
})();
