///////////// field variables /////////////

var previous_obj = null;
const colors = load_colors() // this maps a criterium strength to a color




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

    if (criteria_with_strength_selects.includes(id)) {
        add_strength_selection(id)
    }
}

function update_criteria_description(div, id) {
    //var criteria = ['pvs1', 'ps1', 'ps2', 'ps3', 'ps4', 'pm1', 'pm2', 'pm3', 'pm4', 'pm5', 'pm6', 'pp1', 'pp2', 'pp3', 'pp4', 'pp5', 'ba1', 'bs1', 'bs2', 'bs3', 'bs4', 'bp1', 'bp2', 'bp3', 'bp4', 'bp5', 'bp6', 'bp7']
    const mask = document.getElementById('mask').value;
    var text = criteria_descriptions[mask][id]
    div.textContent = text
}

function update_criteria_evidence_dom(criteria_evidence_dom, previous_evidence) {
    criteria_evidence_dom.value = previous_evidence
}

function update_select_criterium_button(select_criterium_button, id) {
    select_criterium_button.value = id // save the criterium in button such that it knows which one to select on press
    select_criterium_button.checked = document.getElementById(id).checked
}

function add_strength_selection(criterium_id) {
    var additional_content = document.getElementById('additional_content');
    if (criterium_id[0] === 'p') {
        additional_content.innerHTML = `
        <h5 class="bst">Strength:</h5>
        <div>
            <div class="form-check form-check-inline">
                <input class="form-check-input" type="radio" name="strength_select" id="pp_radio" value="pp" onclick="update_criterium_strength(this, '` + criterium_id + `')">
                <label class="form-check-label" for="pp_radio">supporting</label>
            </div>
            <div class="form-check form-check-inline">
                <input class="form-check-input" type="radio" name="strength_select" id="pm_radio" value="pm" onclick="update_criterium_strength(this, '` + criterium_id + `')">
                <label class="form-check-label" for="pm_radio">moderate</label>
            </div>
            <div class="form-check form-check-inline">
                <input class="form-check-input" type="radio" name="strength_select" id="ps_radio" value="ps" onclick="update_criterium_strength(this, '` + criterium_id + `')">
                <label class="form-check-label" for="ps_radio">strong</label>
            </div>
            <div class="form-check form-check-inline">
                <input class="form-check-input" type="radio" name="strength_select" id="pvs_radio" value="pvs" onclick="update_criterium_strength(this, '` + criterium_id + `')">
                <label class="form-check-label" for="pvs_radio">very strong</label>
            </div>
        </div>
        `
    } else {
        if (criterium_id[0] === 'b') {
            additional_content.innerHTML = `
            <h5 class="bst">Strength:</h5>
            <div>
                <div class="form-check form-check-inline">
                    <input class="form-check-input" type="radio" name="strength_select" id="bp_radio" value="bp" onclick="update_criterium_strength(this, '` + criterium_id + `')">
                    <label class="form-check-label" for="bp_radio">supporting</label>
                </div>
                <div class="form-check form-check-inline">
                    <input class="form-check-input" type="radio" name="strength_select" id="bs_radio" value="bs" onclick="update_criterium_strength(this, '` + criterium_id + `')">
                    <label class="form-check-label" for="bs_radio">strong</label>
                </div>
                <div class="form-check form-check-inline">
                    <input class="form-check-input" type="radio" name="strength_select" id="ba_radio" value="ba" onclick="update_criterium_strength(this, '` + criterium_id + `')">
                    <label class="form-check-label" for="ba_radio">stand-alone</label>
                </div>
            </div>
            `
        }
    }
    // preselect
    const preselected_strength = document.getElementById(criterium_id + '_strength').value
    document.getElementById(preselected_strength + '_radio').checked = true
}



// this submits the classification(s)
function submit_classification() {
    // this is important to save the last edited criteria. Otherwise the user 
    // needs to first select some other criterium to save the progress
    save_criteria() 
}


///////////// preselect user classification ////////////
preselect_user_classification()
function preselect_user_classification() {
    document.getElementById('final_class').value = previous_classification
}


///////////// mask select action /////////////
// call function once on page load
preselect_mask()
function preselect_mask() {
    var mask_select = document.getElementById('mask')
    if (variant_genes.includes('TP53') || variant_genes.includes('tp53')) {
        mask_select.value = 'TP53'
    } else if (variant_genes.includes('CDH1') || variant_genes.includes('cdh1')) {
        mask_select.value = 'CDH1'
    } else {
        mask_select.value = 'none'
    }
}

// call the function once to preselect on page load
mask_select_action()
function mask_select_action() {
    revert_all()
    const mask = document.getElementById('mask').value
    set_default_strengths(default_strengths[mask])
    preselect_from_previous_selection(mask)
    set_activatable_property(not_activateable_buttons[mask])
    enable_disable_buttons(not_activateable_buttons[mask], true)

    update_classification_preview()
    update_reference_link(mask)
    update_last_submitted_date(mask)
}

function set_default_strengths(strengths) {
    var all_strength_selects = document.querySelectorAll('[id$="_strength"]');
    for (var i = 0; i < all_strength_selects.length; i++) {
        var current_strength_select = all_strength_selects[i];
        var current_criterium_id = current_strength_select.id.replace('_strength', '');
        current_strength_select.setAttribute('default_strength', strengths[current_criterium_id])
        current_strength_select.value = current_strength_select.getAttribute('default_strength')
    }
}

function preselect_from_previous_selection(mask) {
    const current_mask_with_info = masks_with_info[mask]
    if (typeof current_mask_with_info !== "undefined") { // only preselect if there is data for it
        selected_criteria = current_mask_with_info['selected_criteria']
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

function update_reference_link(mask) {
    document.getElementById('mask_reference').setAttribute('href', reference_links[mask])
}

function update_last_submitted_date(mask) {
    var date = '-'
    const current_mask_with_info = masks_with_info[mask]
    if (typeof current_mask_with_info !== "undefined") { // only preselect if there is data for it
        date = current_mask_with_info['date']
    }
    //document.getElementById('submitted_at_date').textContent = date
}






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

function revert_all() {
    //revert_strength_selects()
    revert_criteria_container()
    revert_buttons()
    revert_previous_obj()
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

function get_currently_checked_criteria() {
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
    var selected_criteria = get_currently_checked_criteria(); // this is an array of criteria ids
    selected_criteria = selected_criteria.join('+')
    fetch('/calculate_acmg_class?selected_classes='+selected_criteria).then(function (response) {
        return response.json();
    }).then(function (text) {
        const final_class = text.final_class
        document.getElementById('classification_preview').textContent = final_class
        if (has_classification === 'False') {
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
    const current_disable_group = disable_groups[criterium_id]
    enable_disable_buttons(current_disable_group, obj.checked)
}

function set_criterium(criterium_id, is_checked) {
    var obj = document.getElementById(criterium_id)
    obj.checked = is_checked
    update_criterium_button_background(criterium_id)
    document.getElementById(criterium_id + '_strength').checked = obj.checked
    const current_disable_group = disable_groups[criterium_id]
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






function preselect_from_data(){
    // TODO!!
}


