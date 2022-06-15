$(document).ready(function() {
    if ($('#reference-genome').val() == null){
        $('#reference-genome').css('color','gray');
    }
    $('#reference-genome').change(function() {
       var current = $('#reference-genome').val();
       if (current != 'null') {
           $('#reference-genome').css('color','black');
       } else {
           $('#reference-genome').css('color','gray');
       }
    }); 
 });