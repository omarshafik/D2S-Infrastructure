from mysql.connector import (connection)
import json

tables = {}
tables['workbench'] = (
    "CREATE TABLE IF NOT EXISTS `WORKBENCH` ("
    "   `wb_id` INT(8) NOT NULL AUTO_INCREMENT,"
    "   `name` VARCHAR(200) NOT NULL,"
    "   `directory` VARCHAR(200) NOT NULL,"
    "   `date` DATETIME NOT NULL,"
    "   `version` VARCHAR(20) NOT NULL,"
    "   `total_runtime` INT(8) NOT NULL,"
    "   `clock_time` INT(8) NOT NULL,"
    "   `passed_tests_num` INT(8),"
    "   `failed_tests_num` INT(8),"
    "   PRIMARY KEY (`wb_id`)"
    ") ENGINE=InnoDB"
)
tables['test'] = (
    "CREATE TABLE IF NOT EXISTS `TEST` ("
    "   `t_id` INT(8) NOT NULL AUTO_INCREMENT,"
    "   `wb_id` INT(8) NOT NULL,"
    "   `name` VARCHAR(200) NOT NULL,"
    "   `is_passed` BOOL NOT NULL,"
    "   `reason` VARCHAR(20),"
    "   `realtime` INT(8) NOT NULL,"
    "   PRIMARY KEY (`t_id`),"
    "   FOREIGN KEY (wb_id) REFERENCES WORKBENCH(wb_id)"
    ") ENGINE=InnoDB"
)

with open("./db_credentials.json") as credentialsFile:
    credentials = json.load(credentialsFile)

cnx = connection.MySQLConnection(**credentials)

cursor = cnx.cursor()
cursor.execute(tables['workbench'])
cursor.execute(tables['test'])
cursor.execute("SHOW TABLES")

print("==========================================================================")
print("Tables created")
print("==========================================================================\n")
for (table_name,) in cursor:
    print(table_name)
print("\n==========================================================================")

cursor.close()
cnx.close()