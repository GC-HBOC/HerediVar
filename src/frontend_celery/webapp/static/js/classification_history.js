
table = document.getElementById("historyTable");
if (table != null) {
    sorter(['#date_col', '#type_col'], '#historyTable') // sort first by num of flags and if there is a tie sort by length
}