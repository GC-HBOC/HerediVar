
//////////////////////////////////////////////////////////////
////////////////// activating functionality //////////////////
//////////////////////////////////////////////////////////////

$(document).ready(function()
{
    // form validation
    // listens on the class validationreq
    $(".validationreq").focus(function(){
        $(this).parent().removeClass("was-validated");
    });
    $(".validationreq").blur(function(){
        if ($(this).attr('type') !== 'checkbox'){ // do not show validation colors for checkboxes as they should be fine no matter what you tick!
            $(this).parent().addClass("was-validated");
            $(".form-control:valid").parent().removeClass("was-validated");
        }
    });

    // add default row to all empty tables
    $(".table").map(function() {
        var nrows = $(this).find("tbody").find("tr").length
        if (nrows === 0) {
            add_default_caption($(this).get(0))
        }
    });

    // activate bootstrap tooltips
    $("body").tooltip({ selector: '[data-bs-toggle=tooltip]' });
    $('.tooltip-lg').tooltip({
        container: 'body',
        template: '<div class="tooltip" role="tooltip"><div class="tooltip-arrow"></div><div class="tooltip-inner tooltip-inner-lg"></div></div>'
    });


    // activate bootstrap popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
      return new bootstrap.Popover(popoverTriggerEl)
    })
    
    // activate table column sorting on click
    $('.sortable').click(function(e) {
        const table_id = '#' + $(this).parents('table').attr('id')
        table_sorter([$(this).parents('th').index()], table_id)
    });

    // functionality for column filters in tables
    $(".column-filter").on("keyup", function() {
        var table = $(this).parents('table').get(0)
        //var index = $(this).parents('th').index()
        filterTable_multiple_columns($(this).val(), table, true)
    });

    // activate links on EVERY object
    $("*[data-href]").click(function(event) {
        switch (event.which) {
            case 1: // left mouse button
                window.location = $(this).data("href"); // open link in same tab
                break;
            case 3: // right mouse button
                // nothing rn
                break;
        }
    });

    // activate middle mouse button links
    // mousedown is preferred here because middle mouse button also triggers
    // fast scrolling on mousedown
    $("*[data-href]").mousedown(function(event) {
        switch (event.which) {
            case 2: // middle mouse button
                window.open($(this).data("href")); // open in new tab
                break;
        }
    });


    // coloring of consensus classification
    document.getElementsByName('class-label').forEach(function(obj) {
        const possible_classes = ["1", "2", "3", "4", "5"]
        var consensus_classification = obj.getAttribute('classification').trim();
        if (!possible_classes.includes(consensus_classification)) {
            consensus_classification = "none"
            tooltip_text = "This variant has not been classified by the VUS task-force yet."
        } else {
            tooltip_text = "This variant has been classified by the VUS task-force with the class " + consensus_classification
        }

        $(obj).addClass("classification_" + consensus_classification + "_col")

    
        obj.querySelector("#theC").setAttribute('title', tooltip_text);
    });

    document.getElementsByName('consensus_class_display').forEach(function(obj) {
        const possible_classes = ["1", "2", "3", "4", "5"]
        var consensus_classification = obj.getAttribute('classification').trim()
        if (!possible_classes.includes(consensus_classification)) {
            consensus_classification = "none"
            tooltip_text = "This variant has not been classified by the VUS task-force yet."
        } else {
            tooltip_text = "This variant has been classified by the VUS task-force with the class " + consensus_classification
        }

        $(obj).addClass("classification_" + consensus_classification + "_col")
    });
});
