var previous_selected_variants = flask_data.dataset.previousSelectedVariants.split(',');
const do_select_all_variants = flask_data.dataset.selectAllVariants == "true"

$(document).ready(function(){

    

    // add select column to list variant view
    var variant_table = $('#variantTable')
    variant_table.find('thead').find('tr').prepend('<th class="text_align_center bold width_minimal">Select</th>')
    variant_table.find('tbody').find('tr').each(function(){
        var trow = this
        var variant_id = trow.getAttribute("variant_id")
        create_select_check(trow, variant_id)
    });

    // functionality for the select all check
    document.getElementById("select_all_variants").addEventListener("click", function() { // add event listenter
        select_all_variants()
        previous_selected_variants = []
    })
    if (do_select_all_variants) { // preselect the select all check from previous request
        document.getElementById("select_all_variants").checked = true
        select_all_variants()
    } else {
        document.getElementById("select_all_variants").checked = false
    }

    // preselect the single variant checks
    const variant_selects = document.getElementsByClassName("variant_select") 
    for (var i = 0; i < variant_selects.length; i++) {
        var current_variant_select = variant_selects[i]
        if (previous_selected_variants.includes(current_variant_select.value)) {
            current_variant_select.checked = !do_select_all_variants
        }
    }

    // this adds the selected variants to the uri of the pagination links once the user clicks it
    const page_links = document.getElementsByClassName("page-link")
    for (var i = 0; i < page_links.length; i++) {
        page_links[i].addEventListener("click", function() {
            new_url = add_selected_variants_to_uri(this.getAttribute('href'))
            this.setAttribute('href', new_url)
        })
    }

    // add the selected variants to the form submission when the user clicks a list
    const list_submit_forms = document.getElementsByClassName("submit_from_list_button")
    for (var i = 0; i < list_submit_forms.length; i++) {
        list_submit_forms[i].addEventListener("click", function() {
            const the_form = this.parentNode
            var current_action = the_form.action
            var new_action = add_selected_variants_to_uri(current_action)
            the_form.action = new_action
        })
    }

    const publish_submit_button = document.getElementById("publish_submit_button")
    publish_submit_button.addEventListener("click", function() {
        const the_form = this.parentNode.parentNode
        var current_action = the_form.action
        var new_action = add_selected_variants_to_uri(current_action)
        the_form.action = new_action
    })
});





function select_all_variants() {
    const all_selected = document.getElementById("select_all_variants").checked
    const variant_checkboxes = document.getElementsByClassName("variant_select")
    for (var i = 0; i < variant_checkboxes.length; i++) {
        var current_checkbox = variant_checkboxes[i]
        current_checkbox.checked = all_selected
    }
}



function get_selected_variants() {
    const all_selected = document.getElementById("select_all_variants").checked
    const variant_checkboxes = document.getElementsByClassName("variant_select")
    var variant_ids = []

    for (var i = 0; i < variant_checkboxes.length; i++) {
        var current_checkbox = variant_checkboxes[i]

        if ((all_selected && !current_checkbox.checked) || (!all_selected && current_checkbox.checked)) {
            var variant_id = current_checkbox.value
            variant_ids.push(variant_id)
        }
    }
    return variant_ids
}
function get_unselected_variants() {
    const all_selected = document.getElementById("select_all_variants").checked
    const variant_checkboxes = document.getElementsByClassName("variant_select")
    var variant_ids = []

    for (var i = 0; i < variant_checkboxes.length; i++) {
        var current_checkbox = variant_checkboxes[i]

        if ((!all_selected && !current_checkbox.checked && previous_selected_variants.includes(current_checkbox.value)) || (all_selected && current_checkbox.checked && previous_selected_variants.includes(current_checkbox.value))) {
            var variant_id = current_checkbox.value
            variant_ids.push(variant_id)
        }
    }
    return variant_ids
}
function get_final_selected_variants() {
    const new_selected_variants = get_selected_variants()
    const new_unselected_variants = get_unselected_variants()
    var selected_variants = [...new Set(new_selected_variants.concat(previous_selected_variants))]
    selected_variants = selected_variants.filter( ( el ) => !new_unselected_variants.includes( el ) ); // remove unselected varaints
    return selected_variants
}


function add_selected_variants_to_uri(url) {
    // get list of selected variants
    const selected_variants = get_final_selected_variants()
    
    // get url
    var new_url = new URL(url, "https://localhost")
    new_url.searchParams.set('selected_variants', selected_variants.filter(item => item).join(','))
    new_url.searchParams.set('select_all_variants', document.getElementById('select_all_variants').checked)
    new_url = new_url.href.substring(new_url.origin.length)
    return new_url
}






function create_select_check(parent, variant_id) {
    //<td class="text_align_center"><input class="form-check-input variant_select" type="checkbox" value="{{ variant.id }}" autocomplete="off"></td>
    var td = document.createElement("td")
    td.classList.add('text_align_center')
    parent.insertBefore(td, parent.firstChild)

    var input = document.createElement("input")
    input.classList.add("form-check-input")
    input.classList.add("variant_select")
    input.setAttribute("type", "checkbox")
    input.value = variant_id
    input.setAttribute("autocomplete", "off")
    td.appendChild(input)

    input.addEventListener("click", function() {
        get_final_selected_variants()
    })
}