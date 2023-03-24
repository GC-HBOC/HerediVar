

const lists = JSON.parse(document.getElementById("targetid").dataset.lists);

for (var i = 0; i < lists.length; i++) {
    current_list = lists[i]
    if (current_list[3] == 1 || current_list[5] == 1) {
        var list_id = lists[i][0]
        var list_name = lists[i][2]
        lists[i] = [list_id, list_name]
    }
}

autocomplete(document.getElementById("lookup_list_name"), document.getElementById("lookup_list_id"), lists);

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
