///////////// field variables /////////////

var previous_obj = null;
const colors = load_colors() // this maps a criterium strength to a color which are defined in css

///////////// prepare data ////////////
const schemes_with_info = json_string_to_object(schemes_with_info_string)
const request_form = json_string_to_object(request_form_string)
var do_request_form_preselect = false
if (Object.keys(request_form).length > 0) {
    do_request_form_preselect = true
}

///////////// criterium buttons /////////////

function button_select_action(obj){
    obj.checked = ! obj.checked;

    save_criteria()

    const id = obj.id;
    const previous_evidence = obj.value;
    update_info_panel(id, previous_evidence)

    previous_obj = obj
}

function save_criteria() {
    if (previous_obj != null) {
        previous_obj.value = document.getElementById('criteria_evidence').value
    }
}

function update_info_panel(id, previous_evidence) {
    revert_criteria_container()
    //var criteria_container = document.getElementById('criteria_container')
    var criteria_title = document.getElementById('criteria_title')
    criteria_title.textContent = id.toUpperCase();
    document.getElementById('button_container').hidden = false;

    $('#select_criterium_check').popover('hide')
    document.getElementById('select_criterium_check').hidden = false;

    var criteria_description_dom = document.getElementById('criteria_description')
    update_criteria_description(criteria_description_dom, id)
    var criteria_evidence_dom = document.getElementById('criteria_evidence')
    update_criteria_evidence_dom(criteria_evidence_dom, previous_evidence)
    var select_criterium_button = document.getElementById('select_criterium_check')
    update_select_criterium_button(select_criterium_button, id)


    
    if (classification_type === 'consensus') {
        add_user_acmg_classification_details(id)
    }

    if (criteria_with_strength_selects.includes(id)) {
        add_strength_selection(id)
    }


}

function update_criteria_description(div, id) {
    const scheme = document.getElementById('scheme').value;
    var text = criteria_descriptions[scheme][id]
    div.textContent = text
}

function update_criteria_evidence_dom(criteria_evidence_dom, previous_evidence) {
    criteria_evidence_dom.value = previous_evidence
}

function update_select_criterium_button(select_criterium_button, id) {
    select_criterium_button.value = id // save the criterium in button such that it knows which one to select on press
    select_criterium_button.checked = document.getElementById(id).checked
}

function criterium_strength_to_description(criterium_strength) {
    criterium_strength = criterium_strength.toLowerCase()
    if (criterium_strength == 'pvs') {
        return 'very strong'
    }
    if (criterium_strength == 'ps') {
        return 'strong'
    }
    if (criterium_strength == 'pm') {
        return 'medium'
    }
    if (criterium_strength == 'pp') {
        return 'supporting'
    }
    if (criterium_strength == 'bp') {
        return 'supporting'
    }
    if (criterium_strength == 'bs') {
        return 'strong'
    }
    if (criterium_strength == 'ba') {
        return 'stand-alone'
    }
}


// this submits the classification(s)
function submit_classification() {
    // this is important to save the last edited criteria. Otherwise the user 
    // needs to first select some other criterium to save the progress
    save_criteria() 
}


///////////// preselect stuff ////////////
// call functions once on page load
function preselect_final_classification() {
    document.getElementById('final_class').value = previous_classification
}


function preselect_scheme() {
    var scheme_select = document.getElementById('scheme')
    if (variant_genes.includes('TP53') || variant_genes.includes('tp53')) {
        scheme_select.value = 'acmg_TP53'
    } else if (variant_genes.includes('CDH1') || variant_genes.includes('cdh1')) {
        scheme_select.value = 'acmg_CDH1'
    } else {
        scheme_select.value = 'acmg_standard'
    }
}

//Object.keys(request_form).length
function preselect_from_request_form() {
    document.getElementById('final_class').value = request_form['final_class']
    document.getElementById('comment').value = request_form['comment']
    document.getElementById('scheme').value = request_form['scheme']

    for (var key in request_form) {
        if (criteria.includes(key)) { // filter for criteria
            set_criterium(key, true)
            var current_evidence = request_form[key]
            document.getElementById(key).value = current_evidence

            var current_strength = request_form[key + '_strength']
            set_criterium_strength(key, current_strength)

            update_criterium_button_background(key)

        }
    }
}



$(document).ready(function() {

    if (do_request_form_preselect) {
        preselect_from_request_form()
    } else {
        preselect_final_classification()
        preselect_scheme()
    }

    scheme_select_action(do_revert=!do_request_form_preselect)

});



// call the function once to preselect on page load
// we need to wait until the document is ready to call the function because there is some jquery
// which will not be loaded if this function is called without the document ready!
function scheme_select_action(do_revert=true) {
    if (do_revert) {
        revert_all()
    }
    
    const scheme = document.getElementById('scheme').value
    if (scheme == 'none') {
        $('#classification_schema_wrapper').collapse('hide');
        //classification_schema_wrapper_div.classList.remove('show')
    } else {
        $('#classification_schema_wrapper').collapse('show');
        set_default_strengths(default_strengths[scheme])
        set_activatable_property(not_activateable_buttons[scheme])
        enable_disable_buttons(not_activateable_buttons[scheme], true)
    
        if (classification_type === 'user' && do_revert) {
            preselect_criteria_from_database(scheme)
        }
        if (classification_type === 'consensus') {
            set_user_selection_counts(scheme)
        }
        
        update_classification_preview()
        update_reference_link(scheme)
        //update_last_submitted_date(scheme)
        
        //update_schemes_with_info()
    }
}

function set_user_selection_counts(scheme) {
    for (var user_id in schemes_with_info) {
        var current_schemes_with_info = schemes_with_info[user_id]
        var scheme_with_info = current_schemes_with_info[scheme] ?? {} // get an empty dict if the user does not have a user classification for this scheme
        var selected_criteria = scheme_with_info['selected_criteria'] ?? {} // propagate the above
        for (var i in selected_criteria) {
            var criterium = selected_criteria[i]
            var criterium_id = criterium[2]
            var count_label = document.getElementById('users_selected_' + criterium_id)
            count_label.innerText = parseInt(count_label.innerText) + 1
            count_label.hidden = false;
        }
    }
}

function set_default_strengths(strengths) {
    var all_strength_selects = document.querySelectorAll('[id$="_strength"]');
    for (var i = 0; i < all_strength_selects.length; i++) {
        var current_strength_select = all_strength_selects[i];
        var current_criterium_id = current_strength_select.id.replace('_strength', '');
        current_strength_select.setAttribute('default_strength', strengths[current_criterium_id])
        if (!Object.keys(request_form).includes(current_criterium_id) || request_form['scheme'] !== document.getElementById('scheme').value) {
            current_strength_select.value = current_strength_select.getAttribute('default_strength')
        }   
    }
}

function preselect_criteria_from_database(scheme) {
    const user_id = Object.keys(schemes_with_info)[0]
    const current_scheme_with_info = schemes_with_info[user_id][scheme]
    if (typeof current_scheme_with_info !== "undefined") { // only preselect if there is data for it
        selected_criteria = current_scheme_with_info['selected_criteria']
        for(var i = 0; i < selected_criteria.length; i++) {
            var current_data = selected_criteria[i];
            var current_criterium = current_data[2].toLowerCase();
            var current_evidence = current_data[4];
            var current_strength = current_data[3];

            var selected_button = document.getElementById(current_criterium);
            selected_button.value = current_evidence;
            set_criterium_strength(current_criterium, current_strength)
            set_criterium(current_criterium, true)
        }
    }
}

function set_activatable_property(criterium_ids) {
    for (var i = 0; i < criterium_ids.length; i++) {
        var criterium_id = criterium_ids[i];
        var current_criterium_button = document.getElementById(criterium_id)
        current_criterium_button.setAttribute('activateable', 'false')
    }
}

function update_reference_link(scheme) {
    document.getElementById('scheme_reference').setAttribute('href', reference_links[scheme])
}

//function update_last_submitted_date(scheme) {
//    var date = '-'
//    const current_scheme_with_info = schemes_with_info[scheme]
//    if (typeof current_scheme_with_info !== "undefined") { // only preselect if there is data for it
//        date = current_scheme_with_info['date']
//    }
//    //document.getElementById('submitted_at_date').textContent = date
//}





///////////// revert state /////////////

function revert_criteria_container() {
    document.getElementById('criteria_title').textContent = "Please select a criterion";
    document.getElementById('select_criterium_check').checked = false;
    document.getElementById('select_criterium_check').hidden = true;
    document.getElementById('button_container').hidden = true;
    document.getElementById('criteria_description').textContent = "";
    document.getElementById('criteria_evidence').value = "";
    document.getElementById('additional_content').innerHTML = "";
}

function revert_buttons() {
    var all_buttons = document.querySelectorAll('.btn-check')
    for (var i = 0; i < all_buttons.length; i++) {
        var current_button = all_buttons[i];
        current_button.checked = false;
        current_button.value = ""
        current_button.setAttribute('activateable', 'true')
        current_button.disabled = false
        update_criterium_button_background(current_button.id)
    }
}

function revert_strength_selects() {
    var all_buttons = document.querySelectorAll('.btn-check')
    for (var i = 0; i < all_buttons.length; i++) {
        var current_button_id = all_buttons[i].id;
        var current_strength_select = document.getElementById(current_button_id + '_strength')
        current_strength_select.value = current_strength_select.getAttribute('default_strength') // this extracts the default strength of the criterium
    }
}

function revert_previous_obj() {
    previous_obj = null;
}

function revert_count_labels() {
    var all_count_labels = document.querySelectorAll('.count_label')
    for (var i in all_count_labels) {
        var current_count_label = all_count_labels[i]
        current_count_label.innerText = '0'
        current_count_label.hidden = true
    }
}

function revert_all() {
    //revert_strength_selects()
    revert_criteria_container()
    revert_buttons()
    revert_previous_obj()
    revert_count_labels()
}


//////////// create dom object functions ////////////
// strength select radio buttons
function add_strength_selection(criterium_id) {
    var additional_content = document.getElementById('additional_content');
    const new_subcaption = create_subcaption('Strength:')
    additional_content.appendChild(new_subcaption)
    if (criterium_id[0] === 'p') {
        var container = document.createElement('div')
        container.appendChild(create_strength_ratio(criterium_id, 'pp'))
        container.appendChild(create_strength_ratio(criterium_id, 'pm'))
        container.appendChild(create_strength_ratio(criterium_id, 'ps'))
        container.appendChild(create_strength_ratio(criterium_id, 'pvs'))
        additional_content.appendChild(container)
    } else {
        if (criterium_id[0] === 'b') {
            var container = document.createElement('div')
            container.appendChild(create_strength_ratio(criterium_id, 'bp'))
            container.appendChild(create_strength_ratio(criterium_id, 'bs'))
            container.appendChild(create_strength_ratio(criterium_id, 'ba'))
            additional_content.appendChild(container)
        }
    }
    // preselect
    const preselected_strength = document.getElementById(criterium_id + '_strength').value
    document.getElementById(preselected_strength + '_radio').checked = true
}

function create_strength_ratio(criterium_id, criterium_strength) {
    var container = document.createElement('div')
    container.classList.add('form-check')
    container.classList.add('form-check-inline')

    var radio = document.createElement('input')
    radio.classList.add('form-check-input')
    radio.type = 'radio'
    radio.name = 'strength_select'
    radio.id = criterium_strength + '_radio'
    radio.value = criterium_strength
    radio.onchange = function() {update_criterium_strength(this, criterium_id)}
    container.appendChild(radio)

    var label = document.createElement('label')
    label.classList.add('form-check-label')
    label.setAttribute('for', radio.id)
    label.innerText = criterium_strength_to_description(criterium_strength)
    container.appendChild(label)
    return container
}

function create_table_data(text) {
    var new_td = document.createElement('td')
    new_td.appendChild(document.createTextNode(text))
    return new_td
}

// consensus classification specific
function create_user_acmg_details_table() {
    var table_container = document.createElement('div')
    table_container.classList.add('table-responsive')

    var table = document.createElement('table')
    table.classList.add('table')
    table.classList.add('table-hover')
    table.classList.add('scroll')
    table_container.appendChild(table)

    var header = document.createElement('thead')
    var header_row = document.createElement('tr')
    header_row.appendChild(create_sortable_header('User'))
    header_row.appendChild(create_sortable_header('Affiliation'))
    header_row.appendChild(create_sortable_header('Strength'))
    var evidence_header = create_sortable_header('Evidence')
    evidence_header.setAttribute('style', 'width:100%')
    header_row.appendChild(evidence_header)
    header_row.appendChild(create_sortable_header('Date'))
    header_row.appendChild(create_non_sortable_header('Copy evidence'))
    header.appendChild(header_row)
    table.appendChild(header)

    var body = document.createElement('tbody')
    body.id = "user_acmg_details"
    table.appendChild(body)
    return table_container
}

function create_non_sortable_header(text) {
    var new_th = document.createElement('th')
    new_th.innerText = text
    return new_th
}

function create_sortable_header(text) {
    var new_th = document.createElement('th')
    
    var title = document.createElement('div')
    title.classList.add('sortable')
    title.innerText = text
    new_th.appendChild(title)

    var searchbar = document.createElement('input')
    searchbar.type = 'text'
    searchbar.classList.add('form-control')
    searchbar.classList.add('form-control-sm')
    searchbar.classList.add('column-filter')
    searchbar.classList.add('sst')
    searchbar.setAttribute('placeholder', 'search...')
    new_th.appendChild(searchbar)
    return new_th
}

function create_subcaption(text) {
    var new_subcaption = document.createElement('h5')
    new_subcaption.appendChild(document.createTextNode(text))
    new_subcaption.classList.add('bst')
    return new_subcaption
}

// this returns one row of the user scheme table shown when making a consensus classification
function create_row_user_acmg_details(user, affiliation, strength, evidence, date) {
    var new_row = document.createElement('tr')
    new_row.appendChild(create_table_data(user))
    new_row.appendChild(create_table_data(affiliation))
    new_row.appendChild(create_table_data(criterium_strength_to_description(strength)))
    new_row.appendChild(create_table_data(evidence))
    new_row.appendChild(create_table_data(date))
    //new_row.appendChild(create_table_data('copy...')) // TODO
    var copy_evidence_td = document.createElement('td')
    copy_evidence_td.setAttribute('style', 'text-align:center;')
    var copy_evidence_text = document.createElement('div')
    // add the bootstrap icon
    copy_evidence_text.innerHTML = `
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="currentColor" class="bi bi-clipboard-plus" viewBox="0 0 16 16">
            <path fill-rule="evenodd" d="M8 7a.5.5 0 0 1 .5.5V9H10a.5.5 0 0 1 0 1H8.5v1.5a.5.5 0 0 1-1 0V10H6a.5.5 0 0 1 0-1h1.5V7.5A.5.5 0 0 1 8 7z"/>
            <path d="M4 1.5H3a2 2 0 0 0-2 2V14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V3.5a2 2 0 0 0-2-2h-1v1h1a1 1 0 0 1 1 1V14a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V3.5a1 1 0 0 1 1-1h1v-1z"/>
            <path d="M9.5 1a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5h-3a.5.5 0 0 1-.5-.5v-1a.5.5 0 0 1 .5-.5h3zm-3-1A1.5 1.5 0 0 0 5 1.5v1A1.5 1.5 0 0 0 6.5 4h3A1.5 1.5 0 0 0 11 2.5v-1A1.5 1.5 0 0 0 9.5 0h-3z"/>
        </svg>
    `
    copy_evidence_text.value = evidence
    copy_evidence_text.setAttribute('strength', strength)
    copy_evidence_text.onclick = function() {copy_evidence(this)}
    copy_evidence_text.classList.add('clickable')
    copy_evidence_td.appendChild(copy_evidence_text)
    new_row.appendChild(copy_evidence_td)
    return new_row
}

// functionality of the copy evidence 'buttons'
function copy_evidence(obj) {
    var evidence_input = document.getElementById('criteria_evidence')
    evidence_input.value = obj.value
    const strength_to_select = obj.getAttribute('strength')

    var radio_to_select = document.getElementById(strength_to_select + '_radio')
    if (radio_to_select != null) {
        radio_to_select.click()
    }
}

function add_user_acmg_classification_details(criterium_id) {
    const scheme = document.getElementById('scheme').value
    var additional_content = document.getElementById('additional_content')
    const new_subcaption = create_subcaption("User selections:")
    additional_content.appendChild(new_subcaption)

    // add the table
    const tab = create_user_acmg_details_table()
    additional_content.appendChild(tab)
    for (var user_id in schemes_with_info) {
        var current_schemes_with_info = schemes_with_info[user_id]
        var user = current_schemes_with_info['user']['2'] + ' ' + current_schemes_with_info['user'][3]
        var affiliation = current_schemes_with_info['user'][4]
        var scheme_with_info = current_schemes_with_info[scheme]
        if (typeof scheme_with_info !== 'undefined') {
            var current_date = scheme_with_info['date']
            var selected_criteria = scheme_with_info['selected_criteria'] // (28, 4, 'bs1', 'bs', 'fdsaf')
            for (var i in selected_criteria) {
                var criterium = selected_criteria[i]
                var current_criterium_id = criterium[2]
                var current_strength = criterium[3]
                var current_evidence = criterium[4]
                if (current_criterium_id === criterium_id) {
                    var new_row = create_row_user_acmg_details(user, affiliation, current_strength, current_evidence, current_date)
                    document.getElementById('user_acmg_details').appendChild(new_row)
                }
            }
        }

    }
    add_functionality_to_table()
}

// this stuff is usually called on page load but needs to be refreshed here because the table
// is generated from javascript and does not exist on page load!
function add_functionality_to_table() {
    // add default row to all empty tables
    $(".table").map(function() {
        var nrows = $(this).find("tbody").find("tr").length
        if (nrows === 0) {
            add_default_caption($(this).get(0))
        }
    });
    ////////// functionality for column filters in tables
    $(".column-filter").on("keyup", function() {
        var table = $(this).parents('table').get(0)
        var index = $(this).parents('th').index()
        filterTable_one_column($(this).val(), index, table, true)
    });

    $('.sortable').click(click_sorter);
}






///////////// helper functions /////////////

function select_criterium(obj) {
    const criterium_id = obj.value // this is the criterium which we want to select
    var criterium_to_select_dom = document.getElementById(criterium_id)
    if (document.getElementById('criteria_evidence').value.trim() == '' && !criterium_to_select_dom.checked) { 
        $('#' + obj.id).popover('show')
        obj.checked = false;
    } else { // only select criterium if there is evidence
        $('#' + obj.id).popover('hide')
        set_criterium(criterium_id, obj.checked)
        //criterium_to_select_dom.checked = !criterium_to_select_dom.checked
        update_classification_preview()
    }
}

function get_checked_criteria_strengths() {
    var result = []
    var all_buttons = document.querySelectorAll('.btn-check')
    for (var i = 0; i < all_buttons.length; i++) {
        var current_button = all_buttons[i];
        if (current_button.checked) {
            var new_value = document.getElementById(current_button.id + '_strength').value
            result.push(new_value)
        }
    }
    return result
}

function get_currently_checked_criteria() {
    var result = []
    var all_buttons = document.querySelectorAll('.btn-check')
    for (var i = 0; i < all_buttons.length; i++) {
        var current_button = all_buttons[i];
        if (current_button.checked) {
            result.push(current_button.id)
        }
    }
    return result
}

function load_colors() {
    const red = $('.btn-red').css('color')
    const orange = $('.btn-orange').css('color')
    const yellow = $('.btn-yellow').css('color')
    const green = $('.btn-green').css('color')
    const blue = $('.btn-blue').css('color')
    const purple = $('.btn-purple').css('color')
    const darkblue = $('.btn-darkblue').css('color')
    return {'pvs': red, 'ps': orange, 'pm': yellow, 'pp': green, 'bp': blue, 'bs': purple, 'ba': darkblue}
}

function enable_disable_buttons(criterium_ids, is_disable) {
    for (var i = 0; i < criterium_ids.length; i++) {
        var current_criterium_id = criterium_ids[i];
        var current_criterium_button = document.getElementById(current_criterium_id)
        // this is just a sanity check to make sure that the disabled buttons are not checked!
        if (current_criterium_button.checked) {
            set_criterium(current_criterium_id, false)
        }
        if (current_criterium_button.getAttribute('activateable') === 'true') {
            current_criterium_button.disabled = is_disable
        } else {
            current_criterium_button.disabled = true
        }
    }
}

function update_classification_preview() {
    var selected_criteria = get_checked_criteria_strengths(); // this is an array of criteria ids
    selected_criteria = selected_criteria.join('+')
    fetch('/calculate_acmg_class/'+selected_criteria).then(function (response) {
        return response.json();
    }).then(function (text) {
        const final_class = text.final_class
        document.getElementById('classification_preview').textContent = final_class
        if (has_classification === 'False' && !do_request_form_preselect) {
            document.getElementById('final_class').value = final_class
        }
        
    });
}

function update_criterium_button_background(criterium_id) {
    var criterium_button = document.getElementById(criterium_id);
    var criterium_strength_select = document.getElementById(criterium_id + '_strength');
    var criterium_label = document.getElementById(criterium_id + '_label');

    var outer_color = colors[criterium_strength_select.value];
    //var inner_color = colors[criterium_id.replace(/\d+/g,'')]

    if (!criterium_button.checked) {
        criterium_label.style['background-color'] = null
    } else {
        criterium_label.style['background-color'] = outer_color //"radial-gradient(circle, " + inner_color + " 50%, " + outer_color + " 100%)"
    }
}

// select and unselect the criterium itself + its associated strength input check which holds information about its user-assigned strenght
function toggle_criterium(criterium_id) {
    var obj = document.getElementById(criterium_id)
    obj.checked = !obj.checked
    update_criterium_button_background(criterium_id)
    document.getElementById(criterium_id + '_strength').checked = obj.checked
    const scheme = document.getElementById('scheme').value
    const current_disable_group = disable_groups[scheme][criterium_id]
    enable_disable_buttons(current_disable_group, obj.checked)
}

function set_criterium(criterium_id, is_checked) {
    var obj = document.getElementById(criterium_id)
    obj.checked = is_checked
    update_criterium_button_background(criterium_id)
    document.getElementById(criterium_id + '_strength').checked = obj.checked
    const scheme = document.getElementById('scheme').value
    const current_disable_group = disable_groups[scheme][criterium_id]
    enable_disable_buttons(current_disable_group, obj.checked)
}

function set_criterium_strength(criterium_id, strength) {
    document.getElementById(criterium_id + '_strength').value = strength;
}

function update_criterium_strength(obj, criterium_id) {
    var strength_obj = document.getElementById(criterium_id + '_strength')
    strength_obj.value = obj.value
    update_classification_preview()
    update_criterium_button_background(criterium_id)
}


//
//function update_schemes_with_info() {
//    const scheme = document.getElementById('scheme').value
//
//    var currently_checked_criteria = get_currently_checked_criteria()
//    var new_selection = []
//    for (var i in currently_checked_criteria) {
//        var criterium_id = currently_checked_criteria[i]
//        var current_evidence = document.getElementById(criterium_id).value
//        var current_strength = document.getElementById(criterium_id + '_strength').value
//        new_selection.push([-1,-1,criterium_id, current_strength, current_evidence])
//    }
//    schemes_with_info['selected'][scheme] = {'selected_criteria': new_selection}
//}
//



function preselect_from_data(){
    // TODO!!
}


