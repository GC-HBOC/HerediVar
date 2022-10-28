
// presort table on page load
table = document.getElementById("historyTable");
if (table != null) {
    table_sorter(['#date_col', '#type_col'], '#historyTable') // sort first by num of flags and if there is a tie sort by length
}