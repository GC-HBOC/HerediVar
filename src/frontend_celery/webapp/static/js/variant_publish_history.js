// presort table on page load
table = document.getElementById("variant_import_history_table");
if (table != null) {
    table_sorter(['#requestedatcol'], '#variant_import_history_table') // sort first by num of flags and if there is a tie sort by length
}