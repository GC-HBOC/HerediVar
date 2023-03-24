
$(document).ready(function() {
    orphanet_codes = JSON.parse(document.getElementById('flask_data').dataset.orphanetCodes)['orphanet_codes']
    autocomplete(document.getElementById("orpha_name"), document.getElementById('orpha_code'), orphanet_codes);
});



