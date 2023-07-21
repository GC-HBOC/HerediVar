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
    

    $('#select_all_jobs').click(function() {
        const checked_state = this.checked
        $('input[name="job"]').each(function() {
            if (! this.disabled) {
                this.checked = checked_state
            }  
        })
    })



    // Activate datatables
    $('#warningstable thead th').each(function() {
        var new_search_input = document.createElement('input')
        new_search_input.setAttribute('placeholder', 'search...')
        new_search_input.classList.add('w_100')
        $(this).append(new_search_input)
    });
     
    // DataTable
    var warnings_table = $('#warningstable').on("draw.dt", function () {
        $(this).find(".dataTables_empty").parents('tbody').empty();
    }).DataTable({
        order: [[0, 'desc']]
    });
     
    // Apply the search
    warnings_table.columns().eq(0).each(function(colIdx) {
        $('input', warnings_table.column(colIdx).header()).on('keyup change', function() {
            warnings_table
                .column(colIdx)
                .search(this.value)
                .draw();
        });
        
        $('input', warnings_table.column(colIdx).header()).on('click', function(e) {
            e.stopPropagation();
        });
    });


    // Activate datatables
    $('#errortable thead th').each(function() {
        var new_search_input = document.createElement('input')
        new_search_input.setAttribute('placeholder', 'search...')
        new_search_input.classList.add('w_100')
        $(this).append(new_search_input)
    });
     
    // DataTable
    var error_table = $('#errortable').on("draw.dt", function () {
        $(this).find(".dataTables_empty").parents('tbody').empty();
    }).DataTable({
        order: [[0, 'desc']]
    });
     
    // Apply the search
    error_table.columns().eq(0).each(function(colIdx) {
        $('input', error_table.column(colIdx).header()).on('keyup change', function() {
            error_table
                .column(colIdx)
                .search(this.value)
                .draw();
        });
        
        $('input', error_table.column(colIdx).header()).on('click', function(e) {
            e.stopPropagation();
        });
    });

    $("#errortable");


});
