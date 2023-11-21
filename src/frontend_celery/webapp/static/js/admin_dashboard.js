$(document).ready(function()
{

    const flask_data = document.getElementById('flask_data')
    const hide_scheme_url = flask_data.dataset.hideSchemeUrl
    const set_default_scheme_url = flask_data.dataset.setDefaultSchemeUrl


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



    //functionality for the hide scheme switches
    $('.hide_scheme_switch').on("click", function(e) {
        const scheme_id = e['target'].getAttribute('scheme_id');
        const is_active = e['target'].checked;
        $.ajax({
            type: 'POST',
            url: hide_scheme_url,
            data: {'scheme_id': scheme_id,
                   'is_active': is_active},
            success: function(data, status, request) {
                console.log(data)
                
            },
            error: function() {
                console.log('error')
            }
        });
    });

    $(".set_default_scheme_radio").on("click", function(e) {
        const scheme_id = e['target'].value
        $.ajax({
            type: 'POST',
            url: set_default_scheme_url,
            data: {'scheme_id': scheme_id},
            success: function(data, status, request) {
                console.log(data)
                
            },
            error: function() {
                console.log('error')
            }
        });
    })

    
    table_sorter(['#scheme_id_column'], '#scheme_table')


});
