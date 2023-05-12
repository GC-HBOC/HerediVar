
const flask_data = document.getElementById("flask_data")
const lists = JSON.parse(flask_data.dataset.lists);
const list_names = JSON.parse(flask_data.dataset.listNames);
const list_ids = JSON.parse(flask_data.dataset.listIds);

for (var i = 0; i < lists.length; i++) {
    current_list = lists[i]
    if (current_list[3] == 1 || current_list[5] == 1) {
        var list_id = lists[i][0]
        var list_name = lists[i][2]
        lists[i] = [list_id, list_name]
    }
}


// functionality for the bed file upload           
function changeStatus(status) {
    document.getElementById('status').innerHTML = status;
}

function loaded(e) {
    const fr = e.target;
    var bed_text = fr.result;
    var text_area = document.getElementById('ranges')
    // append to text area
    bed_lines = bed_text.split(/\r\n|\n/);
    bed_lines.forEach((line) => {
        line = line.trim()
        if (line.startsWith('chr')) {
            parts = line.split('\t')
            if (parts.length >= 3 ) {
                text_area.value = text_area.value + '\n' + parts[0] + ':' + parts[1] + '-' + (parts[2] - 1)
            }
        }
    })
    text_area.value = text_area.value.trim()
}

function errorHandler(e) {
    changeStatus('Error: ' + e.target.error.name);
}

document.getElementById('bed').addEventListener('change', function(e) {
    const file = document.getElementById('bed').files[0];
    
    if (file) {
        const fr = new FileReader();

        fr.readAsText(file);
        fr.addEventListener('loadend', loaded);
        fr.addEventListener('error', errorHandler);
    }
});

// save state of collapse in cookie such that it stays open if the user reloads the page (eg. upon search)
document.getElementById("advanced_search").addEventListener("show.bs.collapse", function(e) {
    var active = 'advanced_search';
    localStorage.setItem('expandedSearchOptions', active);
});

document.getElementById("advanced_search").addEventListener("hide.bs.collapse", function(e) {
    localStorage.removeItem('expandedSearchOptions');
});

var last = localStorage.getItem('expandedSearchOptions');
if (last != null) {
    //remove default collapse settings
    document.getElementById("advanced_search").classList.add('show');
    //show collapse
    document.getElementById(last).classList.add('show');
}


var loadbed_button = document.getElementById('loadbed')
loadbed_button.onclick = function() {document.getElementById('bed').click()}
var selected_bedfile_input = document.getElementById('bed')
selected_bedfile_input.onchange = function() { document.getElementById('filepath_display').innerText = 'selected: ' + this.value.replace(/.*[\/\\]/, '') }


document.getElementById("add_list_select").addEventListener("click", function(e) {
    create_list_select(document.getElementById("select_list_wrapper"))
})
function create_list_select(parent, list_id = "", list_name = "") {
    /*
        <div class="autocomplete full_page">
            <input id="lookup_list_id" name="lookup_list_id" class="visually_hidden" type="text" value="{{ request.args.get('lookup_list_id', '') }}">
            <input value="{{ request.args.get('lookup_list_name', '') }}" id="lookup_list_name" class="form-control" name="lookup_list_name" type="text" placeholder="Select a list... start search by typing">
        </div>
    */
    const wrapper = document.createElement('div')
    wrapper.classList.add("autocomplete")
    wrapper.classList.add("full_page")
    wrapper.classList.add("d-flex")
    parent.appendChild(wrapper)

    const id_input = document.createElement("input")
    id_input.setAttribute("name", "lookup_list_id")
    id_input.classList.add("visually_hidden")
    id_input.setAttribute("type", "text")
    id_input.value = list_id
    wrapper.appendChild(id_input)

    const text_input = document.createElement("input")
    text_input.setAttribute("name", "lookup_list_name")
    text_input.classList.add("form-control")
    text_input.setAttribute("type", "text")
    text_input.setAttribute("placeholder", "Select a list... start search by typing")
    text_input.value = list_name
    wrapper.appendChild(text_input)

    const delete_button = document.createElement("button")
    delete_button.setAttribute("type", "button")
    delete_button.addEventListener("click", function(e) {
        wrapper.remove()
    })
    delete_button.classList.add("btn")
    delete_button.classList.add("btn-light")
    delete_button.appendChild(create_trashcan())
    wrapper.appendChild(delete_button)

    autocomplete(text_input, id_input, lists);
}


if (list_names.length == list_ids.length) {
    for (var i = 0; i < list_ids.length; i++) {
        current_list_id = list_ids[i]
        current_list_name = list_names[i]
        if (current_list_id != "" && current_list_name != "") {
            create_list_select(document.getElementById("select_list_wrapper"), list_id= current_list_id, list_name = current_list_name)
        }
    }
}
if (document.getElementsByName("lookup_list_name").length == 0) {
    create_list_select(document.getElementById("select_list_wrapper"))
}