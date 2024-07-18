$(document).ready(function() {
    if ($('#reference_genome').val() == null){
        $('#reference_genome').css('color','gray');
    }
    $('#reference_genome').change(function() {
       var current = $('#reference_genome').val();
       if (current != 'null') {
           $('#reference_genome').css('color','black');
       } else {
           $('#reference_genome').css('color','gray');
       }
    }); 
 });