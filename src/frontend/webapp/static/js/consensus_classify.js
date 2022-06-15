
$(document).ready(function()
{
    var dropdowns = $('.expandible-list')
    for (var i = 0; i < dropdowns.length; i++) {
        var dropdown = dropdowns[i]
        var selected = $(dropdown).is(':checked');
        console.log(selected)
        if (selected) {
            var dest = $(dropdown).attr('href')
            $(dest).collapse("show");
        }
    }

    // disable checkboxes if animation is going on for the expandible lists
    // this prevents that double clicking the checkbox makes collapse and checkbox asynchronous!
    $('.collapse').on('show.bs.collapse hide.bs.collapse', function() {
        $('.expandible-list').prop('disabled', true);
    }).on('shown.bs.collapse hidden.bs.collapse', function() {
        $('.expandible-list').prop('disabled', false);
    });

    

});