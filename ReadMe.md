# D2S Software Infrastructure Engineer Task  

### Files Description:  
* read_logs.py: main script  
* read_logs_definitions.py: functions and constants used in read_logs.py  
* initialize_database.py: script to initialize the database with required tables
* db_credentials.json: credentials used by scripts to connect to database (configured by user)
### The main script **read_logs.py** has different functionalities.  

1. Parse tests logs and save it to JSON file; use -j argument.  
2. Parse tests logs and save it to MySQL database; use -s argument.  
3. Parse tests logs and display it in a tabular format and save formatted logs to csv files; use -t argument.  
4. Query on saved formatted logs in the database by (test name and version) or by test version only; use -q combined with --name and the test name to find and/or --version and the test version to find.  
5. Display saved formatted logs in double bar charts with version and date on x-axis; use -g argument.  

Notes:  
* to read all log files from a directory use -i INPUT_DIRECTORY argument.
* to specify output directory use -o OUTPUT_DIRECTORY argument.
* to read only one file use -f FILE_PATH argument.
* use |`python3 read_logs.py -h`| for help.