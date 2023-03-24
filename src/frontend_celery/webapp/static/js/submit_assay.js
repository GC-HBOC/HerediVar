


$(document).ready(function(){
    on_page_load()

    $('#assay_type').click(function() {
        select_assay_type_action(this.value);
    });
});



function on_page_load() {
    const assay_type_select = document.getElementById('assay_type')
    assay_type_select.value = assay_type_select.getAttribute('initvalue')
    select_assay_type_action(assay_type_select.getAttribute('initvalue'))
}




function select_assay_type_action(assay_type) {
    var score_label_obj = document.getElementById('score_label')

    if (assay_type !== '') {
        document.getElementById('report_form_group').hidden=false
        document.getElementById('score_form_group').hidden=false
    }

    if (assay_type === 'functional') {
        score_label_obj.innerText = "Functional assay score"
    } else if (assay_type === 'splicing') {
        score_label_obj.innerText = "Splicing assay score"
    }
}