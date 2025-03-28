
$(document).ready(function()
{
    // parse flask data
    const flask_data = document.getElementById("special_flask_data")
    var user_lists = JSON.parse(flask_data.dataset.lists)
    var variant_base_url = flask_data.dataset.variantBaseUrl
    const page = flask_data.dataset.page
    const page_size = flask_data.dataset.pageSize 
    const base_delete_action_url = flask_data.dataset.deleteAction
    const view_list = flask_data.dataset.viewList
    const generate_list_vcf_url = flask_data.dataset.generateListVcfUrl
    const generate_list_vcf_status_url = flask_data.dataset.generateListVcfStatusUrl

    // edit / create button functionality
    $('#list-modal-submit').click(function(){
        $('#create-list-button').attr('disabled', true);
        /* when the submit button in the modal is clicked, submit the form */
        $('#list-modal-form').submit();
    });

    $('#generate_list_vcf_button').click(function(){
        //document.getElementById("export_to_vcf_worker").click()
        console.log(generate_list_vcf_url)
        $.ajax({
            type: 'GET',
            url: generate_list_vcf_url,
            success: function(returnval, status, request) {
                show_vcf_gen_status('bg-secondary', "Annotation requested successfully", "Annotation requested")
                update_vcf_generation_status(generate_list_vcf_status_url);
            },
            error: function(xhr, status, error) {
                console.log(xhr)
                show_vcf_gen_status("bg-danger", "The variant could not be annotated. Either the service is unreachable or some other unexpected exception occured. You can try to reload this page or issue another annotation to fix this. If that does not help try again later. Status code is: " + xhr.status, "Internal error")
                $('#reannotate_button').attr('disabled', false)
            }
        });
    });
    update_vcf_generation_status(generate_list_vcf_status_url)

    var list_id = $('#current-list-id')[0].innerText

    // delete button functionality
    $('#list-modal-submit-delete').click(function(){
        var form_to_submit = $('#list-modal-form')
        form_to_submit.attr('action', '/mylists?type=delete_list')
        form_to_submit.submit();
    });

    // add delete and numbering column to list variant view
    var variant_table = $('#variantTable')
    variant_table.find('thead').find('tr').append('<th class="text_align_center bold width_minimal">Del</th>')
    variant_table.find('thead').find('tr').prepend('<th class="text_align_center bold width_minimal">#</th>')
    const list_permissions = $('#list-permissions')
    const can_edit = list_permissions.attr('data-owner') == 1 || list_permissions.attr('data-editable') == 1 
    var number = 1 + ((page-1) * page_size)
    variant_table.find('tbody').find('tr').each(function(){
        var trow = $(this)
        var variant_id = trow[0].getAttribute("variant_id")
        var variant_url = variant_base_url.replace('0', variant_id)
        prepend_number_td(trow, variant_url, number)
        if (can_edit) {
            create_delete_button(trow, base_delete_action_url, variant_id)
        } else {
            create_xlg(trow, "You can not delete this variant from the list because you do not have edit rights on the list.")
        }
        number = number + 1
    });
    activate_data_href_links()

    // add event listeners
    $('#public_read').change(function() {
        public_read_toggle_action()
    })

    
    // parse lists
    for (var i = 0; i < user_lists.length; i++) {
        current_list = user_lists[i]
        if (current_list[3] == 1 || current_list[5] == 1) {
            var list_id = user_lists[i][0]
            var list_name = user_lists[i][2]
            user_lists[i] = [list_id, list_name]
        }
    }
    autocomplete(document.getElementById("other_list_name"), document.getElementById("other_list_id"), user_lists);

    $('#inplace').change(function() {
        const modal = document.getElementById('createModal')
        list_name_obj = modal.querySelector('#list_name_obj')
        public_read_obj = modal.querySelector('#public_read_obj')
        public_edit_obj = modal.querySelector('#public_edit_obj')
        if (!this.checked) {
            show_obj(list_name_obj)
            show_obj(public_read_obj)
            show_obj(public_edit_obj)
        } else {
            hide_obj(list_name_obj)
            hide_obj(public_read_obj)
            hide_obj(public_edit_obj)
        }
    })
});




//<div class="ssb">
//{% if generate_list_vcf_status is not none %} <!--requested_at, status, finished_at, message, is_valid-->
//    {% if list_import_status[1] == 'pending' %}
//        <span class="badge rounded-pill bg-secondary" data-bs-toggle="tooltip" title="VCF generation requested at {{ generate_list_vcf_status[0] }}. Waiting for worker to pick it up.">VCF gen requested</span>
//    {% endif %}
//    {% if list_import_status[1] == 'success' %}
//        <span class="badge rounded-pill bg-success" data-bs-toggle="tooltip" title="VCF generation requested finished successfully at {{ generate_list_vcf_status[2] }}">VCF gen successful</span>
//    {% endif %}
//    {% if list_import_status[1] == 'error' %}
//        <span class="badge rounded-pill bg-danger" data-bs-toggle="tooltip" title="VCF generation finished at {{ generate_list_vcf_status[2] }} with fatal error {{ generate_list_vcf_status[3] }}">VCF gen error</span>
//    {% endif %}
//    {% if list_import_status[1] == 'retry' %}
//        <span class="badge rounded-pill bg-warning" data-bs-toggle="tooltip" title="VCF generation yielded an error. Retrying soon: {{ generate_list_vcf_status[3] }}">VCF gen retry</span>
//    {% endif %}
//    {% if list_import_status[1] == 'aborted' %}
//        <span class="badge rounded-pill bg-warning" data-bs-toggle="tooltip" title="VCF generation was aborted">VCF gen aborted</span>
//    {% endif %}
//    {% if list_import_status[1] == 'progress' %}
//        <span class="badge rounded-pill bg-primary" data-bs-toggle="tooltip" title="The VCF generation is processed in the background. Please wait until it is finished.">VCF gen aborted</span>
//    {% endif %}
//{% else %}
//    <span class="badge rounded-pill bg-secondary" data-bs-toggle="tooltip" title="VCF generation is required if you want to download the list in VCF format">No VCF</span>
//{% endif %}
//</div>


// polling & status display update
function update_vcf_generation_status(status_url) {
    // send GET request to status URL (defined by flask)
    $.ajax({
        type: 'GET',
        url: status_url,
        success: function(data, status, request) {
            console.log(data)
            if (data === undefined) {
                show_vcf_gen_status("bg-secondary", "VCF generation is required if you want to download the list in VCF format. You can generate one through the gear button.", "No VCF")
            } else if (data["is_valid"] == 0) {
                show_vcf_gen_status("bg-secondary", "VCF generation is required if you want to download the list in VCF format. You can generate one through the gear button.", "No VCF")
            } else {
                if (data['status'] == 'pending') {
                    show_vcf_gen_status("bg-secondary", "VCF generation is queued. This job is waiting for other jobs to finish first.", "VCF gen queued")
                } else if (data['status'] == 'progress') {
                    show_vcf_gen_status("bg-primary", "VCF generation is being processed in the background. Please wait for it to finish.", "VCF gen processing")
                } else if (data['status'] == "success") {
                    show_vcf_gen_status("bg-success", "VCF generation finished at " + data["finished_at"], "VCF gen success")
                } else if (data['status'] == "error") {
                    show_vcf_gen_status("bg-danger", "VCF generation annotation finished at " + data["finished_at"] + " with fatal error: " + data['message'], "VCF gen error")
                } else if (data['status'] == 'retry') {
                    show_vcf_gen_status("bg-warning", "Task yielded an error: " + data['error_message'] + ". Will try again soon.", "Retrying VCF gen")
                } else if (data['status'] == 'aborted') {
                    show_vcf_gen_status("bg-primary", "This task was manually aborted at " + data['finished_at'], "VCF gen aborted")
                } else if (data['status'] == 'no_vcf') {
                    show_vcf_gen_status("bg-secondary", "VCF generation is required if you want to download the list in VCF format. You can generate one through the gear button.", "No VCF")
                } else {
                    show_vcf_gen_status("bg-warning", "An unexpected status found: " + data['status'], "Unexpected status")
                    //$('#reannotate_button').attr('disabled', false);
                }

                // polling happens here:
                // rerun in 5 seconds if state resembles an unfinished task
                if (data['status'] == 'pending' || data['status'] == 'progress' || data['status'] == 'retry') {
                    setTimeout(function() {
                        update_vcf_generation_status(status_url);
                    }, 5000);
                }
            }
        },
        error: function(xhr) {
            show_vcf_gen_status("bg-danger", "Unable to fetch the status. Server returned http status " + xhr.status, "Internal error")
            $('#reannotate_button').attr('disabled', false)
        }
    })

}

function show_vcf_gen_status(color_class, tooltip_text, inner_text) {
    const pill_holder_id = "vcf_gen_pill_holder"
    const pill_id = "vcf_gen_pill"
    show_status(color_class, tooltip_text, inner_text, pill_holder_id, pill_id)
}





function create_delete_button(parent, base_delete_action_url, variant_id) {
    /*
    This is what the following should look like in html:
    <td style="text-align:center;"> 
        <form action="/mylists?view=list_id&type=delete_variant&variant_id=variant_id" method="post" novalidate>
            <button type="submit" class="btn btn-link" style="padding:0;">
                <svg id="delete-from-list-button" xmlns="http://www.w3.org/2000/svg" width="17" height="17" fill="red" class="bi bi-trash3" viewBox="0 0 16 16"> 
                    <path d="M6.5 1h3a.5.5 0 0 1 .5.5v1H6v-1a.5.5 0 0 1 .5-.5ZM11 2.5v-1A1.5 1.5 0 0 0 9.5 0h-3A1.5 1.5 0 0 0 5 1.5v1H2.506a.58.58 0 0 0-.01 0H1.5a.5.5 0 0 0 0 1h.538l.853 10.66A2 2 0 0 0 4.885 16h6.23a2 2 0 0 0 1.994-1.84l.853-10.66h.538a.5.5 0 0 0 0-1h-.995a.59.59 0 0 0-.01 0H11Zm1.958 1-.846 10.58a1 1 0 0 1-.997.92h-6.23a1 1 0 0 1-.997-.92L3.042 3.5h9.916Zm-7.487 1a.5.5 0 0 1 .528.47l.5 8.5a.5.5 0 0 1-.998.06L5 5.03a.5.5 0 0 1 .47-.53Zm5.058 0a.5.5 0 0 1 .47.53l-.5 8.5a.5.5 0 1 1-.998-.06l.5-8.5a.5.5 0 0 1 .528-.47ZM8 4.5a.5.5 0 0 1 .5.5v8.5a.5.5 0 0 1-1 0V5a.5.5 0 0 1 .5-.5Z"/> 
                </svg> 
            </button>
        </form>
    </td>
    */

    var td = document.createElement("td")
    td.classList.add('text_align_center')
    parent[0].appendChild(td)

    var form = document.createElement("form")
    form.setAttribute("action", base_delete_action_url + "&variant_id=" + variant_id)
    form.setAttribute("method", "post")
    td.appendChild(form)

    var button = document.createElement("button")
    button.setAttribute("type", "submit")
    button.classList.add('btn')
    button.classList.add("btn-link")
    button.classList.add("nopad")
    form.appendChild(button)

    image = create_trashcan()
    button.appendChild(image)
}


function prepend_number_td(trow, url, number) {
    var td = document.createElement("td")
    td.classList.add('text_align_center')
    td.classList.add('clickable')
    td.setAttribute('data-href', url)
    td.innerText = number
    trow[0].prepend(td)
}


function public_read_toggle_action() {
    var read_elem = document.getElementById('public_read')
    var edit_elem = document.getElementById('public_edit')
    if (!read_elem.checked) {
        
        edit_elem.checked = false
        edit_elem.disabled = true
    } else {
        edit_elem.disabled = false
    }
}



var create_modal = document.getElementById('createModal')
create_modal.addEventListener('show.bs.modal', function (event) {
    var button = event.relatedTarget
    var action_type = button.getAttribute('data-bs-type')
    var list_name_select = create_modal.querySelector('#list_name')
    var modal_title = create_modal.querySelector('.modal-title')
    var submit_button = create_modal.querySelector('#list-modal-submit')
    var list_id_meta = create_modal.querySelector('#list_id')
    var public_read_toggle = create_modal.querySelector('#public_read')
    var public_edit_toggle = create_modal.querySelector('#public_edit')


    var preselected_list_name = ''
    var title = ''
    var form_action_type = ''
    var submit_button_title = ''
    var list_id = ''

    if (action_type == 'edit') {
        show_modal_content(show_list_name = true, show_permissions = true, show_other_list = false, show_delete_button = true, show_inplace_toggle = false)

        title = 'Edit \"' + button.getAttribute('data-bs-name') + '\"'
        preselected_list_name = button.getAttribute('data-bs-name')
        list_id = button.getAttribute('data-bs-id')
        form_action_type = '/mylists?type=edit'
        submit_button_title = 'Update'
        
        public_read_toggle.checked = ((button.getAttribute('data-bs-public-read') == '1') ? true : false)
        public_edit_toggle.checked = ((button.getAttribute('data-bs-public-edit') == '1') ? true : false)
        public_edit_toggle.disabled = ((button.getAttribute('data-bs-public-read') == '1') ? false : true)
    }

    if (action_type == 'create') {
        show_modal_content(show_list_name = true, show_permissions = true, show_other_list = false, show_delete_button = false, show_inplace_toggle = false)
        title = 'Create a new list'
        form_action_type = '/mylists?type=create'
        submit_button_title = 'Create'
        public_read_toggle.checked = false
        public_edit_toggle.checked = false
        public_edit_toggle.disabled = true
    }

    if (action_type == 'duplicate') {
        show_modal_content(show_list_name = true, show_permissions = true, show_other_list = false, show_delete_button = false, show_inplace_toggle = false)
        title = 'Duplicate list'
        list_id = button.getAttribute('data-bs-id')
        form_action_type = '/mylists?type=duplicate'
        submit_button_title = "Duplicate"
        public_read_toggle.checked = false
        public_edit_toggle.checked = false
        public_edit_toggle.disabled = true
    }

    if (action_type == 'intersect') {
        show_modal_content(show_list_name = true, show_permissions = true, show_other_list = true, show_delete_button = false, show_inplace_toggle = true)
        title = 'Intersect list'
        list_id = button.getAttribute('data-bs-id')
        form_action_type = '/mylists?type=intersect'
        submit_button_title = "Intersect"
        public_read_toggle.checked = false
        public_edit_toggle.checked = false
        public_edit_toggle.disabled = true
    }


    if (action_type == 'subtract') {
        show_modal_content(show_list_name = true, show_permissions = true, show_other_list = true, show_delete_button = false, show_inplace_toggle = true)
        title = 'Subtract list'
        list_id = button.getAttribute('data-bs-id')
        form_action_type = '/mylists?type=subtract'
        submit_button_title = "Subtract"
        public_read_toggle.checked = false
        public_edit_toggle.checked = false
        public_edit_toggle.disabled = true
    }


    if (action_type == 'add') {
        show_modal_content(show_list_name = true, show_permissions = true, show_other_list = true, show_delete_button = false, show_inplace_toggle = true)
        title = 'Add list'
        list_id = button.getAttribute('data-bs-id')
        form_action_type = '/mylists?type=add'
        submit_button_title = "Add"
        public_read_toggle.checked = false
        public_edit_toggle.checked = false
        public_edit_toggle.disabled = true
    }



    modal_title.textContent = title
    submit_button.textContent = submit_button_title
    list_id_meta.setAttribute('value', list_id)
    list_name_select.setAttribute('value', preselected_list_name)
    create_modal.querySelector('#list-modal-form').setAttribute('action', form_action_type)

});


function show_modal_content(show_list_name = true, show_permissions = true, show_other_list = true, show_delete_button = true, show_inplace_toggle = true) {
    const modal = document.getElementById('createModal')
    const list_name_obj = modal.querySelector('#list_name_obj')
    const public_read_obj = modal.querySelector('#public_read_obj')
    const public_edit_obj = modal.querySelector('#public_edit_obj')
    const other_list_obj = modal.querySelector('#other_list_obj')
    const delete_button = modal.querySelector('#list-modal-submit-delete')
    const inplace_toggle_obj = modal.querySelector('#inplace_obj')
    const inplace_toggle = modal.querySelector('#inplace')

    if (show_inplace_toggle) {
        show_obj(inplace_toggle_obj)
        inplace_toggle.checked = false
        inplace_toggle.disabled = false
    } else {
        hide_obj(inplace_toggle_obj)
        inplace_toggle.checked = false
        inplace_toggle.disabled = true
    }
    

    if (show_list_name) {
        show_obj(list_name_obj)
    } else {
        hide_obj(list_name_obj)
    }

    if (show_permissions) {
        show_obj(public_read_obj)
        show_obj(public_edit_obj)
    } else {
        hide_obj(public_read_obj)
        hide_obj(public_edit_obj)
    }

    if (show_other_list) {
        show_obj(other_list_obj)
    } else {
        hide_obj(other_list_obj)
    }

    if (show_delete_button) {
        show_obj(delete_button)
        delete_button.disabled = false
    } else {
        hide_obj(delete_button)
        delete_button.disabled = true
    }

}

function hide_obj(obj) {
    obj.classList.add('visually-hidden')
}

function show_obj(obj) {
    obj.classList.remove('visually-hidden')
}






