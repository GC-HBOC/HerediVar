


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
    $('form').each(function(i, obj) {
        obj.hidden=true;
    })

    if (assay_type !== '') {
        document.getElementById(assay_type + '_assay').hidden=false
    }
}