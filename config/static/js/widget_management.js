$(document).ready(function(){
    // use event delegation for remove widget button
    $(document).on('click', '.remove-widget-btn', function(e){
        e.preventDefault();
        var url = $(this).attr("href");
        $.ajax({
            url: url,
            method: "GET", 
            success: function(response) {
                if (response.success) {
                    alert("Widget removed successfully!");
                    window.location.reload(); 
                } else {
                    alert("Error removing widget: " + response.error);
                }
            },
            error: function(xhr) {
                alert("An error occurred while removing the widget.");
            }
        });
    });

    // initialize sortable on the widget list
    $("#sortable-widgets").sortable({
        placeholder: "ui-state-highlight",
        update: function(event, ui){
            let order = [];
            $(".widget").each(function(){
                order.push($(this).data("widget-id"));
            });
            $("#save-widget-order").data("order", order);
            console.log("New widget order:", order);
        }
    }).disableSelection();

    // save widget order via AJAX
    $("#save-widget-order").click(function(){
        let order = $(this).data("order") || [];
        if (order.length === 0) {
            alert("No changes to save!");
            return;
        }
        $.ajax({
            url: manageDisplayUrl, 
            method: "POST",
            contentType: "application/json",
            headers: { "X-CSRFToken": csrfToken }, 
            data: JSON.stringify({ widget_order: order }),
            success: function(response) {
                alert("Widget order saved successfully!");
                console.log("Server response:", response);
            },
            error: function(xhr) {
                alert("Error saving widget order: " + xhr.responseText);
                console.error("AJAX error:", xhr.responseText);
            }
        });
    });
});
