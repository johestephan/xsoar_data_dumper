# xsoar_data_dumper
XSOAR Data Dumper enables the fetching and storing of incidents from XSOAR. The incidents can be stored in JSON files, CouchDB and MariaDB.
For usability the best choice might be MariaDB, here the ID and Name will match the incident.id and incident.name. Investigation and Incident data will be stored in two seperated fields.

## Usage
    usage: DataDumper.py [-h] [--init] [--run] --auth AUTH --base BASE [--couchdb COUCHDB]

    XSOAR Incident to File.json or CouchDB - data dumper v1

    optional arguments:
      -h, --help         show this help message and exit
      --init             initialise the database
      --run              start downloading incidents
      --auth AUTH        XSOAR Authkey, Credentials
      --base BASE        XSOAR Base URL
      --couchdb COUCHDB  (Optional) use CouchDB https://username:password@host:port/
      --mariadb MARIADB  (Optional) use MariaDB 10.10+ username:password:host:port
      
# Prerequesits
* Authkey of XSOAR (Settings -> Integrations -> Api Keys)
* install requirements.txt (pip3 install -r requirements.txt)
* (Optional) CouchDB Database (https://hub.docker.com/_/couchdb/)

# Details execution
* run with **--init** this will create a local DataDumper.db database (sqlite3) so the script can resume the download
* run with **--run** which will start fetching the incidents
* (Optional) **--couchdb DATA** which will write all incidents into CouchDB instead of files
* (Optional) **--mariadb DATA** will write all incidents into MariaDB (Mysql), it uses JSON tables, so 10.10+ is required

# Cleanup Procedures
* if the scripts stops during **--run** simply run the command again, the script will resume teh Download
* If you need to start from scratch, simply delete the **DataDumper.db** and all files **INCIDENT-*.json** or drop the CouchDB database

# MariaDB
The MariaDB option requires that a database "incidents" has been created before starting a **--run**. The following data structure will be created.

    id INT NOT NULL ,
    name VARCHAR(100) NOT NULL,  
    incident_data JSON ,
    investigation_data JSON, 
    PRIMARY KEY (id

# License

    Copyright 2023 by Joerg Stephan

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
    
# Some Statistics, Disclaimer and results
Tested against 1286 Incidents
* DB folder Size in XSOAR: **2.1GB**, size in Couchdb: **11.2MB**
* Execution time: **1:07:31.66**  (1Hour 7 Minutes)
* The new incident in files or CouchDB will include all incident fields and labels, "Context data" is excluded. For Context data it would be advised to use **!!PrintContext outputformat=json** on XSOAR itself
* Please report bugs and issues via GitHub 
* **Usage at your own risk** but that is also what the License tells you :-)

