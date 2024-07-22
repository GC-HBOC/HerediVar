
const flask_data = document.getElementById("flask_data")
const data_url = flask_data.dataset.getDataUrl;
const vid_details_url = flask_data.dataset.vidDetailsUrl;
const import_queue_id = flask_data.dataset.importQueueId;
const variant_import_summary_url = flask_data.dataset.variantImportSummaryUrl

var first_load = true


$(document).ready(function(){

    toggle_spinners() // show spinners

    activate_datatables("variant_table")

    update_page(data_url)

});


function toggle_spinners() {
    const parent_ids = ["summary_user", "summary_requested_at", "summary_status", "summary_finished_at", "summary_message", "summary_total_num_variants",
                        "variant_summary_pending", "variant_summary_processing", "variant_summary_erroneous", "variant_summary_success", "variant_summary_deleted",
                        "variant_summary_update", "variant_summary_retrying"
                    ]
    parent_ids.forEach(id => {
        var parent = document.getElementById(id)
        var has_spinner = parent.getAttribute("has_spinner") ?? "false"
        
        if (has_spinner === "false") {
            const spinner = create_spinner()
            parent.appendChild(spinner)
            //add_spinner(parent)
            parent.setAttribute("has_spinner", "true")
        } else {
            remove_spinner(parent)
            parent.setAttribute("has_spinner", "false")
        }
        
    });
}


// polling & status display update
function update_page(url) {

    $.getJSON(url, function(data) {

        //console.log(data)
        update_general_information(data)
        update_erroneous_variants(data['imported_variants'])
        update_variant_summary(data["import_request"]["variant_summary"])

        if (first_load) {
            toggle_spinners()
        }

        first_load = false

        // polling happens here:
        // rerun in 5 seconds if state resembles an unfinished task
        const import_status = data["import_request"]["status"]
        if (import_status === "pending" || import_status === "fetching vids" || import_status === "fetching variants" || import_status === "unknown" || import_status === "retry") {
            setTimeout(function() {
                update_page(url);
            }, 10000);
        }
    });

}

const status2meta = {
    "unknown": {"color": "bg-secondary", "tooltip": "Please wait while the status is being fetched."},
    "retry": {"color": "bg-secondary", "tooltip": "There was some unexpected error and the job is retrying now."},
    "pending": {"color": "bg-secondary", "tooltip": "The job is queued and waiting for a worker to be picked up."},
    "fetching vids": {"color": "bg-primary", "tooltip": "The vids are currently fetched from HerediCare."},
    "fetching variants": {"color": "bg-primary", "tooltip": "The vids were fetched from HerediCare. The variants are currently imported to HerediVar."},
    "error": {"color": "bg-danger", "tooltip": "There was an error in this request. See the message below."},
    "finished": {"color": "bg-success", "tooltip": "The variant import is finished."}
}

function update_general_information(data) {
    // update total number of variants
    document.getElementById("summary_total_num_variants").textContent = data["import_request"]["total_variants"]
    
    // update the user
    document.getElementById("summary_user").textContent = data["import_request"]["user"]["full_name"]

    //update the requested date
    document.getElementById("summary_requested_at").textContent = data["import_request"]["requested_at"]

    // update general status
    const the_status = data["import_request"]["status"]
    update_import_status(status2meta[the_status]["color"], status2meta[the_status]["tooltip"], the_status)

    //update finished at date
    document.getElementById("summary_finished_at").textContent = data["import_request"]["finished_at"]

    // update message
    document.getElementById("summary_message").textContent = data["import_request"]["import_variant_list_message"]
}


// utility for showing the current annotation status
function update_import_status(color_class, tooltip_text, inner_text) {
    $('#status_badge').tooltip('hide')
    var status_pill = document.getElementById('status_badge')

    // remove all previous colors
    const current_classes = status_pill.classList
    for (var i = 0; i < current_classes.length; i++) {
        var current_class = current_classes[i]
        if (current_class.indexOf("bg-") >= 0) {
            status_pill.classList.remove(current_class)
        }
    }
    status_pill.classList.remove("visually_hidden")
    status_pill.classList.add(color_class) // add new color
    status_pill.setAttribute('title', tooltip_text)
    status_pill.innerText = inner_text
}



function update_variant_summary(summary_data) {
    all_tds = {"pending": "variant_summary_pending", 
               "progress": "variant_summary_processing",
               "error": "variant_summary_erroneous",
               "success": "variant_summary_success",
               "deleted": "variant_summary_deleted",
               "retry": "variant_summary_retrying",
               "update": "variant_summary_update"
            }
    for (var key in all_tds) {
        var current_td = document.getElementById(all_tds[key])
        if (key in summary_data) {
            current_td.textContent = summary_data[key]
        } else {
            current_td.textContent = "-"
        }
    }
}


function update_erroneous_variants(variants) {
    const table = $('#variant_table').DataTable();
    table.clear().draw(); // remove all rows that are currently there

    for (var i = 0; i < variants.length; i++) {
        var current_variant = variants[i];
        if (current_variant['status'] === "error") {
            var new_trow = create_erroneous_variant_row(current_variant);
            table.row.add(new_trow).draw(false)
        }

    }

    update_default_caption(document.getElementById("variant_table"))
    

}


function create_erroneous_variant_row(variant) {
    const tds = [
        create_td_link(variant["vid"], vid_details_url),
        create_td(variant["status"]),
        create_td(variant["requested_at"]),
        create_td(variant["finished_at"]),
        create_td(variant["message"]),
        create_td_form("retry", variant_import_summary_url, {'import_variant_queue_id': variant['id']})
    ];
    const trow = create_trow(tds);
    return trow;
}

function create_td_form(text_content, url, params) {
    var td = document.createElement('td');

    var form = document.createElement('form')
    form.setAttribute('action', url)
    form.setAttribute('method', 'post')
    td.appendChild(form)

    var new_input = document.createElement('input')
    new_input.value = params['import_variant_queue_id']
    new_input.setAttribute('name', 'import_variant_queue_id')
    new_input.classList.add("visually_hidden")
    form.appendChild(new_input)

    //var tmp = document.createElement('div')
    //tmp.textContent = params['import_variant_queue_id']
    //form.appendChild(tmp)

    var submit_button = document.createElement('button')
    submit_button.classList.add("btn")
    submit_button.classList.add("btn-outline-primary")
    submit_button.textContent = text_content
    form.appendChild(submit_button)

    return td
}

function create_td(text_content) {
    var td = document.createElement('td');
    td.textContent = text_content;
    return td;
}

function create_td_link(text_content, url) {
    var td = document.createElement('td');
    var a = document.createElement('a')
    a.setAttribute('href', url.replace('0', text_content))
    a.textContent = text_content
    td.appendChild(a)
    return td;
}

function create_trow(tds) {
    var trow = document.createElement('tr');
    for (var i = 0; i < tds.length; i++) {
        trow.appendChild(tds[i]);
    }
    return trow;
}


