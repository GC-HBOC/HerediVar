

//////////////////////////////////////////////////////////////
////////////////// activating functionality //////////////////
//////////////////////////////////////////////////////////////

$(document).ready(function()
{
    // presort the tables on page load
    variant_consequence_table_default_sorting_columns = ['#variant_consequence_numflags_col', '#variant_consequence_length_col', '#variant_consequence_gene_symbol_col']
    variant_consequence_table_ascending = ['true', 'true', "false"]
    table = document.getElementById("variantConsequenceTable");
    if (table != null) {
        filterTable_one_column("ensembl", 10, table);
        table_sorter(variant_consequence_table_default_sorting_columns, '#variantConsequenceTable') // sort first by num of flags, at tie by length and at tie by gene symbol
    }
    table_sorter(['#userClassificationsTableDateCol'], '#userClassificationsTable')
    table_sorter(['#literatureTableYearCol'], '#literatureTable')
    table_sorter(['#clinvarSubmissionsTableLastEvaluatedCol'], '#clinvarSubmissionsTable')
    table_sorter(['#heredicareCenterClassificationsTableDateCol'], '#heredicareCenterClassificationsTable')
    table_sorter(['#userSchemeClassificationsTableDateCol'], '#userSchemeClassificationsTable')
    table_sorter(['#assayTableDateCol', '#assayTableAssayTypeCol'], '#assayTable')

    // functionality for the reannotate button
    $('#reannotate-submit').click(function(){
        $('#reannotate_button').attr('disabled', true);
        $('#reannotate-modal').modal('toggle');
        confirm_reannotation_action();
    });

    // functionality for the reload page modal
    $('#reload-submit').click(function() {
        location.reload()
    })

    // functionality to add a variant to a user-list
    $('.variant-list-button').click(function() {
        const form_to_submit = $('#add-to-list-form')
        form_to_submit.attr('action', $(this).attr('action'))
    });

    // set the title of the page
    var variant_page_title_obj = document.getElementById('variant_page_title')
    var title = variant_page_title_obj.innerText
    const ref = variant_page_title_obj.getAttribute('ref')
    const alt = variant_page_title_obj.getAttribute('alt')
    title = get_variant_type(ref, alt) + title
    variant_page_title_obj.innerText = title

    // functionality for the annotation status
    // this is blocking I think so it should be called last!
    var annotation_status = $('#annotation_status').data()['annotationStatus'];
    var celery_task_id = $('#annotation_status').data()['celeryTaskId'];
    if ((annotation_status === 'pending' || annotation_status == 'retry') && celery_task_id !== null){
        $('#reannotate_button').attr('disabled', true)
        //$('#reannotate-list-item').attr('title', "Wait for the current annotation to finish before submitting another one")
        status_url = "/task/annotation_status/" + celery_task_id;
        console.log(status_url)
        update_annotation_status(status_url);
    }
    
});




///////////////////////////////////////////////////////////////////////
////////////////// reannotation button functionality //////////////////
///////////////////////////////////////////////////////////////////////

// function triggered on reannotaiton submit button pressed
function confirm_reannotation_action() {
    // send ajax POST request to start background job
    variant_id = $('#variant_id_container').data()['variantId'];
    $.ajax({
        type: 'POST',
        url: '/task/run_annotation_service?variant_id=' + variant_id,
        success: function(data, status, request) {
            show_annotation_status('bg-secondary', "Annotation requested successfully", "Annotation requested")

            status_url = request.getResponseHeader('annotation_status_url');
            update_annotation_status(status_url);
        },
        error: function() {
            show_annotation_status("bg-danger", "The variant could not be annotated. Either the service is unreachable or some other unexpected exception occured. You can try to reload this page or issue another annotation to fix this. If that does not help try again later.", "Internal error")
            $('#reannotate_button').attr('disabled', false)
        }
    });
}


// polling & status display update
function update_annotation_status(status_url) {
    // send GET request to status URL (defined by flask)
    $.getJSON(status_url, function(data) {
        console.log(data)
        if (data['state'] == 'PENDING') {
            show_annotation_status("bg-secondary", "Annotation is queued. This annotation job is waiting for other jobs to finish first.", "Annotation queued")
        } else if (data['state'] == 'PROGRESS') {
            show_annotation_status("bg-primary", "Annotation is being processed in the background. Please wait for it to finish.", "Annotation processing")
        } else if (data['state'] == "SUCCESS") {
            $('#reload-modal').modal('toggle');
            show_annotation_status("bg-success", "The annotation is finished. Reload the page to see the updated annotations.", "Annotation finished")
        } else if (data['state'] == "FAILURE") {
            show_annotation_status("bg-danger", "Something unexpected happened during variant annotation: " + data['state'] + ' ' + data['status'], "Annotation error")
            $('#reannotate_button').attr('disabled', false);
        } else if (data['state'] == 'RETRY') {
            show_annotation_status("bg-warning", "Task yielded an error: " + data['status'] + ". Will try again soon.", "Retrying annotation")
        } else {
            show_annotation_status("bg-warning", "An unexpected status found: " + data['state'], "Unexpected status")
            $('#reannotate_button').attr('disabled', false);
        }

        // polling happens here:
        // rerun in 5 seconds if state resembles an unfinished task
        if (data['state'] == 'PENDING' || data['state'] == 'PROGRESS' || data['state'] == 'RETRY') {
            
            setTimeout(function() {
                update_annotation_status(status_url);
            }, 5000);
        }
    });
}


// utility for showing the current annotation status
function show_annotation_status(color_class, tooltip_text, inner_text) {
    $('#current_status').tooltip('hide')
    var annotation_status_obj = document.getElementById('annotation_status_pills')
    annotation_status_obj.innerHTML = ""
    // <span class="badge rounded-pill bg-secondary" data-bs-toggle="tooltip" title="annotation requested at {{ current_annotation_status[3] }}">annotation requested, <br> refresh page to see if it is ready</span>
    var status_pill = document.createElement('span')
    status_pill.classList.add('badge')
    status_pill.classList.add('rounded-pill')
    status_pill.classList.add(color_class)
    status_pill.setAttribute('data-bs-toggle', "tooltip")
    status_pill.setAttribute('title', tooltip_text)
    status_pill.innerText = inner_text
    annotation_status_obj.appendChild(status_pill)
    status_pill.id = "current_status"
}




///////////////////////////////////////////////////////////////
////////////////// further utility functions //////////////////
///////////////////////////////////////////////////////////////

// functionality for the consequence table switch between ensembl & refseq
function filter_consequence_table(source) {
    const table = document.getElementById('variantConsequenceTable')
    filterTable_one_column(source, 10, table)
    const sort_columns = variant_consequence_table_default_sorting_columns
    for (var i = 0; i < sort_columns.length; i++) {
        $(sort_columns[i]).attr('asc', variant_consequence_table_ascending[i])
    }
    table_sorter(sort_columns, '#' + table.id)
}


// Infer the variant type by looking at the number of reference and alternative bases
// use this in the header of the page
function get_variant_type(ref, alt) {
    const ref_len = ref.length
    const alt_len = alt.length
    var variant_type = "Variant display" // default phrase just in case
    if (ref_len === 1 && alt_len === 1) {
        variant_type = "SNV"
    }
    if (ref_len > alt_len) {
        variant_type = "Deletion (" + String(ref_len-alt_len) + " bp)"
    }
    if (ref_len < alt_len) {
        variant_type = "Insertion (" + String(alt_len-ref_len) + " bp)"
    }
    return variant_type
}


// multi level dropdown functionality
// move to utils.js?
(function($bs) {
    const CLASS_NAME = 'has-child-dropdown-show';
    $bs.Dropdown.prototype.toggle = function(_orginal) {
        return function() {
            document.querySelectorAll('.' + CLASS_NAME).forEach(function(e) {
                e.classList.remove(CLASS_NAME);
            });
            let dd = this._element.closest('.dropdown').parentNode.closest('.dropdown');
            for (; dd && dd !== document; dd = dd.parentNode.closest('.dropdown')) {
                dd.classList.add(CLASS_NAME);
            }
            return _orginal.call(this);
        }
    }($bs.Dropdown.prototype.toggle);

    document.querySelectorAll('.dropdown').forEach(function(dd) {
        dd.addEventListener('hide.bs.dropdown', function(e) {
            if (this.classList.contains(CLASS_NAME)) {
                this.classList.remove(CLASS_NAME);
                e.preventDefault();
            }
            e.stopPropagation(); // do not need pop in multi level mode
        });
    });

    // for hover
    document.querySelectorAll('.dropdown-hover, .dropdown-hover-all .dropdown').forEach(function(dd) {
        dd.addEventListener('mouseenter', function(e) {
            let toggle = e.target.querySelector(':scope>[data-bs-toggle="dropdown"]');
            if (!toggle.classList.contains('show')) {
                $bs.Dropdown.getOrCreateInstance(toggle).toggle();
                dd.classList.add(CLASS_NAME);
                $bs.Dropdown.clearMenus();
            }
        });
        dd.addEventListener('mouseleave', function(e) {
            let toggle = e.target.querySelector(':scope>[data-bs-toggle="dropdown"]');
            if (toggle.classList.contains('show')) {
                $bs.Dropdown.getOrCreateInstance(toggle).toggle();
            }
        });
    });

    $('.dropdown').on('hidden.bs.dropdown', function() {
        $(this).tooltip("hide");
        //$(this).dropdown('toggle');
    })
})(bootstrap);
