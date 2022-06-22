

$(document).ready(function($){
    var previous_classification = $('#previous_classification').data()['previousClassification'];
    $('#class').val(previous_classification);

    $('#submit-classification-submit').click(function(){
        $('#submit-classification-button').attr('disabled', true);
        /* when the submit button in the modal is clicked, submit the form */
       $('#submit-classification-form').submit();
    });
});
