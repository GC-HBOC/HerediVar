
table = document.getElementById("variantConsequenceTable");
if (table != null) {
    filterTable_one_column("ensembl", 11, table);
    sorter(['#variant_consequence_numflags_col', '#variant_consequence_length_col']) // sort first by num of flags and if there is a tie sort by length
}


$(document).ready(function()
{
    ////////// functionality for the reannotate button
    var annotation_status = $('#annotation_status').data()['annotationStatus'];
    if (annotation_status === 'pending'){
        $('#reannotate_button').attr('disabled', true)
        $('#tooltip_reannotate_button').attr('title', "Wait for the current annotation to finish before submitting another one")
    }

    $('#reannotate-submit').click(function(){
        $('#reannotate_button').attr('disabled', true);
        /* when the submit button in the modal is clicked, submit the form */
       $('#reannotate_form').submit();
    });

    //$('.classification-gradient').css({'background': 'linear-gradient(90deg, ' + class5ColorRGB + ' 0%, rgba(170,240,170,1) 20%, rgba(190,250,190,1) 40%, rgba(255,255,255,1) 100%)'});
    //$('.classification-gradient').css({'background': 'linear-gradient(90deg, rgba(149,149,149,0.5) 0%, rgba(195,195,195,0.5) 20%, rgba(232,232,232,0.5) 40%, rgba(255,255,255,1) 100%)'});
    
});


