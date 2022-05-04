
table = document.getElementById("variantConsequenceTable");
if (table != null) {
    filterTable_one_column("ensembl", 11, table);
    sorter(['#variant_consequence_numflags_col', '#variant_consequence_length_col']) // sort first by num of flags and if there is a tie sort by length
}


$(document).ready(function()
{
    
    ////////// functionality for the reannotate button
    $('#reannotate_button').click(function()
    {
        $(this).attr('disabled', true);
        return true;
    });
    var annotation_status = $('#annotation_status').data()['annotationStatus'];
    if (annotation_status === 'pending'){
        $('#reannotate_button').attr('disabled', true)
        $('#tooltip_reannotate_button').attr('title', "Wait for the current annotation to finish before submitting another one")
    }
});