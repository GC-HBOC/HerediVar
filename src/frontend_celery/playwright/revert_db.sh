# init structure of the database
cat $DB_STRUCTURE | mysql -h $DB_HOST -P $DB_PORT -u$DB_ADMIN -p$DB_ADMIN_PW $DB_NAME 

# init static information
mysql_errors=$(mysql -h $DB_HOST -P $DB_PORT -u$DB_ADMIN -p$DB_ADMIN_PW  $DB_NAME < $DB_STATIC_SEED 2>&1)
if [ $? = "1" ]; then
    echo $mysql_errors
    exit 1
fi
