


$(document).ready(function(){
    on_page_load()

    $('#assay_type_id').click(function() {
        select_assay_type_action(this.value);
    });

});



function on_page_load() {
    const assay_type_select = document.getElementById('assay_type_id')
    assay_type_select.value = assay_type_select.getAttribute('initvalue')
    select_assay_type_action(assay_type_select.getAttribute('initvalue'))
}



function select_assay_type_action(assay_type_id) {
    $('form').each(function(i, obj) {
        obj.hidden=true;
    })

    if (assay_type_id !== '') {
        document.getElementById(assay_type_id + '_assay').hidden=false
    }
}