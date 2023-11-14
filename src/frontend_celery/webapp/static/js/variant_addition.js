const flask_data = document.getElementById("flask_data")
const delete_classification_url = flask_data.dataset.deleteClassificationUrl


// add delete column to list variant view
var classification_table = $('#userClassificationsTable')
classification_table.find('thead').find('tr').append('<th class="text_align_center bold width_minimal">Del</th>')

classification_table.find('tbody').find('tr').each(function(){
    var trow = $(this)
    var variant_id = trow[0].getAttribute("variant_id")
    var user_classification_id = trow[0].getAttribute("user_classification_id")
    var can_delete = trow[0].getAttribute("can_delete")
    if (can_delete === "True") {
        create_delete_button(trow, delete_classification_url, variant_id, user_classification_id)
    } else {
        create_xlg(trow, "You are not allowed to delete this classification")
    }
});
activate_data_href_links()



function create_delete_button(parent, base_url, variant_id, user_classification_id) {
    var td = document.createElement("td")
    td.classList.add('text_align_center')
    parent[0].appendChild(td)

    var button = document.createElement("button")
    button.setAttribute("type", "button")
    button.classList.add('btn')
    button.classList.add("btn-link")
    button.classList.add("nopad")
    button.addEventListener("click", function() {
        delete_user_classification_action(base_url, variant_id, user_classification_id)
    })
    td.appendChild(button)

    image = create_trashcan()
    button.appendChild(image)
}


function delete_user_classification_action(base_url, variant_id, user_classification_id) {
    $.ajax({
        type: "get",
        url: base_url,
        data: {"variant_id": variant_id, "user_classification_id": user_classification_id},
        success: function(data, status, request) {
            console.log(data)

            if (data == "success") {
                $('[user_classification_id="' + user_classification_id + '"]').remove()
            }
            
            console.log($("#userClassificationsTable tr").length)
            
            if ($("#userClassificationsTable tr").length <= 1) {
                $("#heredivar_user_classifications_section").remove()
            }
        },
        error: function() {
            
        }
    });
}