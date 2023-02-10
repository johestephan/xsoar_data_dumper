# xsoar_data_dumper
XSOAR Data Dumper enables the fetching and storing of incidents from XSOAR. They incidents can be stored in JSON files or CouchDB

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
      
# Prerequesits
* Authkey of XSOAR (Settings -> Integrations -> Api Keys)
* install requirements.txt (pip3 install -r requirements.txt)
* (Optional) CouchDB Database (https://hub.docker.com/_/couchdb/)

# Details execution
* run with **--init** this will create a local DataDumper.db database (sqlite3) so the script can resume the download
* run with **--run** which will start fetching the incidents
* Optional **--couchdb DATA** which will write all incidents into CouchDB instead of files

# Disclaimer
This is a free script which has been tested against a small instance (1200 incidents). Please report bugs and issues via GitHub. Usage at your own risk

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
