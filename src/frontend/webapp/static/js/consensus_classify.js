
$(document).ready(function()
{
    $('#submit-submit').click(function(){
        $('#submit-button').attr('disabled', true);
        /* when the submit button in the modal is clicked, submit the form */
       $('#classifyForm').submit();
    });

    // not used ATM
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


// not used atm
// this toggles all checkboxes with specified selecT_group prefix in their name attribute
function toggle_all(source, select_group) {
    checkboxes = document.querySelectorAll('input[name^="' + select_group + '"]');
    //console.log(checkboxes)
    for(var i=0, n=checkboxes.length;i<n;i++) {
        checkboxes[i].checked = source.checked;
    }
}