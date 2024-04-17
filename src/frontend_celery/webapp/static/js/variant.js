$(document).ready(function()
{
    table_sorter(['#userClassificationsTableDateCol'], '#userClassificationsTable')
    table_sorter(['#clinvarSubmissionsTableLastEvaluatedCol'], '#clinvarSubmissionsTable')
    table_sorter(['#heredicareCenterClassificationsTableDateCol'], '#heredicareCenterClassificationsTable')
    table_sorter(['#userSchemeClassificationsTableDateCol'], '#userSchemeClassificationsTable')
    table_sorter(['#assayTableDateCol', '#assayTableAssayTypeCol'], '#assayTable')
    	
    activate_datatables("literatureTable");
});
