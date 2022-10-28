$(document).ready(function()
{
    // functionality for the import & update button

    $('#import-variants-submit').click(function(){
        $('#import-variantsbutton').attr('disabled', true);
        /* when the submit button in the modal is clicked, submit the form */
       $('#import-variants-form').submit();
    });

    $('#reannotate-variants-submit').click(function(){
        $('#reannotate-variantsbutton').attr('disabled', true);
        /* when the submit button in the modal is clicked, submit the form */
       $('#reannotate-variants-form').submit();
    });

});
