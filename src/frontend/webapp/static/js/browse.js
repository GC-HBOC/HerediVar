

$(document).ready(function($){
    $("*[data-href]").on('click', function () {
        window.location = $(this).data("href");
    });

    $('#search_form').submit(function( event ) {
        $('#chosen_search_type').attr('value', $('input[name="search_type"]:checked').val());
    });
    
    $('input[name="search_type"]').on('click', function() {
        var newSearchPlaceholder = $(this).parent().find('label').text()
        if (newSearchPlaceholder !== "Quick search") {
            newSearchPlaceholder += ' search...'
        } else {
            newSearchPlaceholder += '...'
        }
        $('#searchbar').attr('placeholder', newSearchPlaceholder)
    });
});

