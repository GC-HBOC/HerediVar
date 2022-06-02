
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

    ////////// functionality for column filters in tables
    $(".column-filter").on("keyup", function() {
        var table = $(this).parents('table').get(0)
        var index = $(this).parents('th').index()
        filterTable_one_column($(this).val(), index, table, true)
    });

    //$('.classification-gradient').css({'background': 'linear-gradient(90deg, ' + class5ColorRGB + ' 0%, rgba(170,240,170,1) 20%, rgba(190,250,190,1) 40%, rgba(255,255,255,1) 100%)'});
    //$('.classification-gradient').css({'background': 'linear-gradient(90deg, rgba(149,149,149,0.5) 0%, rgba(195,195,195,0.5) 20%, rgba(232,232,232,0.5) 40%, rgba(255,255,255,1) 100%)'});
    

    
    var consensus_classification = document.getElementById('consensusClassificationDIV').textContent.trim()
    switch (consensus_classification) {
        case '5':
            base_color = class5ColorRGB
            console.log(base_color)
            break;
        case '4':
            base_color = class4ColorRGB
            break;
        case '3':
            base_color = class3ColorRGB
            break;
        case '2':
            base_color = class2ColorRGB
            break;
        case '1':
            base_color = class1ColorRGB
            break;
        default:
            base_color = noClassRGB
    }
    $('.classification-gradient').css({'background-color': base_color});
    $('#class-label').css({'color': base_color});

    if (["1", "2", "3", "4", "5"].includes(consensus_classification)) {
        tooltip_text = "This variant has been classified by the VUS task-force with the class " + consensus_classification
    } else {
        tooltip_text = "This variant has not been classified by the VUS task-force yet."
    }

    $('#class-label-tooltip-container').attr('title', tooltip_text);
});


