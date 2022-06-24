

var create_modal = document.getElementById('createModal')
create_modal.addEventListener('show.bs.modal', function (event) {
    var button = event.relatedTarget
    var action_type = button.getAttribute('data-bs-type')
    var list_name_select = create_modal.querySelector('#list-name')
    var modal_title = create_modal.querySelector('.modal-title')
    var submit_button = create_modal.querySelector('#list-modal-submit')
    var list_id_meta = create_modal.querySelector('#list-id')

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
    }

    if (action_type == 'create') {
        title = 'Create a new list'
        form_action_type = '/mylists?type=create'
        submit_button_title = 'Create'
    }

    console.log(form_action_type)

    modal_title.textContent = title
    submit_button.textContent = submit_button_title
    list_id_meta.setAttribute('value', list_id)
    list_name_select.setAttribute('value', preselected_list_name)
    create_modal.querySelector('#list-modal-form').setAttribute('action', form_action_type)

});

$(document).ready(function()
{
    $('#list-modal-submit').click(function(){
        $('#create-list-button').attr('disabled', true);
        /* when the submit button in the modal is clicked, submit the form */
        $('#list-modal-form').submit();
    });


});
