
$(document).ready(function()
{
    // edit / create button functionality
    $('#list-modal-submit').click(function(){
        $('#create-list-button').attr('disabled', true);
        /* when the submit button in the modal is clicked, submit the form */
        $('#list-modal-form').submit();
    });

    var list_id = $('#current-list-id')[0].innerText

    // delete button functionality
    $('#list-modal-submit-delete').click(function(){
        var form_to_submit = $('#list-modal-form')
        form_to_submit.attr('action', '/mylists?type=delete_list')
        form_to_submit.submit();
    });

    // add delete column to list variant view
    var variant_table = $('#variantTable')
    variant_table.find('thead').find('tr').append('<th class="text_align_center bold width_minimal">Del</th>')
    const list_permissions = $('#list-permissions')
    console.log(list_permissions)
    const can_edit = list_permissions.attr('data-owner') == 1 || list_permissions.attr('data-editable') == 1 
    variant_table.find('tbody').find('tr').each(function(){
        var trow = $(this)
        var variant_id = trow[0].getAttribute("variant_id")
        if (can_edit) {
            create_delete_button(trow, list_id, variant_id)
        } else {
            create_xlg(trow)
        }
        
    });

    // add event listeners
    $('#public_read').change(function() {
        public_read_toggle_action()
    })

});



function create_delete_button(parent, list_id, variant_id) {
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
    form.setAttribute("action", "/mylists?view=" + list_id + "&type=delete_variant&variant_id=" + variant_id)
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
    var delete_button = create_modal.querySelector('#list-modal-submit-delete')
    var public_read_toggle = create_modal.querySelector('#public_read')
    var public_edit_toggle = create_modal.querySelector('#public_edit')

    var preselected_list_name = ''
    var title = ''
    var form_action_type = ''
    var submit_button_title = ''
    var list_id = ''

    if (action_type == 'edit') {
        title = 'Edit \"' + button.getAttribute('data-bs-name') + '\"'
        preselected_list_name = button.getAttribute('data-bs-name')
        list_id = button.getAttribute('data-bs-id')
        form_action_type = '/mylists?type=edit'
        submit_button_title = 'Update'
        delete_button.disabled = false
        delete_button.style.visibility = 'visible'
        public_read_toggle.checked = ((button.getAttribute('data-bs-public-read') == '1') ? true : false)
        public_edit_toggle.checked = ((button.getAttribute('data-bs-public-edit') == '1') ? true : false)
        public_edit_toggle.disabled = ((button.getAttribute('data-bs-public-read') == '1') ? false : true)
    }

    if (action_type == 'create') {
        title = 'Create a new list'
        form_action_type = '/mylists?type=create'
        submit_button_title = 'Create'
        delete_button.disabled = true
        delete_button.style.visibility = 'hidden'
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



function create_xlg(parent) {
    var td = document.createElement("td")
    td.classList.add('text_align_center')
    parent[0].appendChild(td)

    var image = document.createElementNS("http://www.w3.org/2000/svg", "svg")
    image.setAttribute('data-bs-toggle', 'tooltip')
    image.setAttribute('title', "You can not delete this variant from the list because you do not have edit rights on the list.")
    image.setAttribute("width", 17)
    image.setAttribute("height", 17)
    image.setAttribute("fill", "red")
    image.classList.add("bi")
    image.classList.add("bi-x-lg")
    image.setAttribute("viewBox", "0 0 16 16")
    td.appendChild(image)

    var path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    path.setAttribute("d", "M2.146 2.854a.5.5 0 1 1 .708-.708L8 7.293l5.146-5.147a.5.5 0 0 1 .708.708L8.707 8l5.147 5.146a.5.5 0 0 1-.708.708L8 8.707l-5.146 5.147a.5.5 0 0 1-.708-.708L7.293 8 2.146 2.854Z")
    image.appendChild(path)
}




