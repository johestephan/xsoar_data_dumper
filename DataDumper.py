# DataDumper to Export XSOAr incidents to .json Files
# Author Joerg Stephan <joerg@johest.de>, 2023
# Version: v1.1

import requests
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import argparse
import sqlite3
import couchdb
import mariadb




def createDB(URLsearch, header):
    con = sqlite3.connect("DataDumper.db")
    cur = con.cursor()
    cur.execute("CREATE TABLE incidents(id, fetched)")
    
    payload = '''{"userFilter":false,"filter":{"page":0,"query":"","size":99999999, "sort":[{"field":"id","asc":false}]}}'''
    indexing = requests.post(URLsearch, data=payload, headers=header, verify=False)
    max_incidents = json.loads(indexing.text)['total']
    pages = int(max_incidents) / 50
    #print(pages)
    for page in range(int(pages)+1):
        payload = '''{"userFilter":false,"filter":{"page":%i,"query":"","size":%i, "sort":[{"field":"id","asc":false}]}}''' % (page, max_incidents)
        indexing = requests.post(URLsearch, data=payload, headers=header, verify=False)
        Jobject = json.loads(indexing.text)
        for line in Jobject.get('data'):
            cur.execute("INSERT INTO incidents VALUES ('%s', 'ToDo')" % line['id'])
            con.commit()
    print("Found %s Incidents (%s Pages Overall)" % (max_incidents, int(pages) + 1))

def datadump_to_couchdb(URLload, URLloadi, header, couchLINK):
    con = sqlite3.connect("DataDumper.db")
    cur = con.cursor()
    res = cur.execute("SELECT id FROM incidents WHERE fetched='ToDo'")
    couch = couchdb.Server(couchLINK)
    payload = ('''{"pageSize": 100}''')
    if not 'incidents' in couch:
        db = couch.create('incidents')
    db = couch['incidents']
    for incid in res.fetchall():
        dataset_investigation = requests.post(URLloadi+incid[0], headers=header, data=payload, verify=False)
        dataset_incident =  requests.get(URLload+incid[0], headers=header, verify=False)
        JObject = json.loads(dataset_incident.text)
        JObject['Investigation'] = json.loads(dataset_investigation.text)
        db.save(JObject)
        cur.execute("UPDATE incidents SET fetched = 'Done' WHERE id = '%s' " % incid[0])
        con.commit()

def datadump_to_mariadb(URLload, URLloadi, header, mariaLINK):
    creds = mariaLINK.split(":")
    conn_params= json.loads('''{
    "user" : "%s",
    "password" : "%s",
    "host" : "%s",
    "port" : %i ,
    "database" : "incidents"}''' % (creds[0], creds[1], creds[2], int(creds[3])))

    connection= mariadb.connect(**conn_params)
    cursor= connection.cursor()
   
    cursor.execute('''create table if not exists incidents (
    id INT NOT NULL ,
    name VARCHAR(100) NOT NULL,  
    incident_data JSON ,
    investigation_data JSON, 
    PRIMARY KEY (id))''')  

    cursor.execute("use incidents")
    con = sqlite3.connect("DataDumper.db")
    cur = con.cursor()
    res = cur.execute("SELECT id FROM incidents WHERE fetched='ToDo'")
    payload = ('''{"pageSize": 100}''')
    for incid in res.fetchall():
        dataset_investigation = requests.post(URLloadi+incid[0], headers=header, data=payload, verify=False)
        dataset_incident =  requests.get(URLload+incid[0], headers=header, verify=False)
        JObject = json.loads(dataset_incident.text)
        JObject2 = json.loads(dataset_investigation.text)
        cursor.execute('''INSERT INTO incidents(id, name, incident_data, investigation_data) VALUES (?, ?, ?, ?)''', 
        [int(incid[0]), str(JObject['name'])[:99], json.dumps(JObject), json.dumps(JObject2)])
        connection.commit()
        

def datadump(URLload, URLloadi, header):
    con = sqlite3.connect("DataDumper.db")
    cur = con.cursor()
    res = cur.execute("SELECT id FROM incidents WHERE fetched='ToDo'")
    payload = ('''{"pageSize": 100}''')
    for incid in res.fetchall():
        dataset_investigation = requests.post(URLloadi+incid[0], headers=header, data=payload, verify=False)
        dataset_incident =  requests.get(URLload+incid[0], headers=header, verify=False)
        JObject = json.loads(dataset_incident.text)
        JObject['Investigation'] = json.loads(dataset_investigation.text)
        outfile = open("INCIDENT-%s.json"% (incid), "w")
        json.dump(JObject, outfile)
        outfile.close()
        cur.execute("UPDATE incidents SET fetched = 'Done' WHERE id = '%s' " % incid[0])
        con.commit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='XSOAR Incident to File.json or CouchDB - data dumper v1')
    parser.add_argument('--init', help='initialise the database', action='store_true')
    parser.add_argument('--run', help='start downloading incidents', action='store_true')
    parser.add_argument('--auth', help='XSOAR Authkey, Credentials', required=True)
    parser.add_argument('--base', help='XSOAR Base URL', required=True)
    parser.add_argument('--couchdb', help='(Optional) use CouchDB https://username:password@host:port/')
    parser.add_argument('--mariadb', help='(Optional) use MariaDB 10.10+ username:password:host:port')

    args = parser.parse_args()
    header = json.loads('''{"Authorization" : "%s", 
          "Content-Type": "application/json", 
          "Accept": "application/json"}''' % (args.auth))
    URLloadi = str(args.base) +"/investigation/"
    URLload = str(args.base) + "/incident/load/"
    URLsearch = str(args.base) + "/incidents/search"
    if args.init:
        createDB(URLsearch, header)
    elif args.run:
        if args.couchdb is not None:
            datadump_to_couchdb(URLload,URLloadi, header, args.couchdb)
        if args.mariadb is not None:
            datadump_to_mariadb(URLload,URLloadi, header, args.mariadb)
        else:
            datadump(URLload, URLloadi, header) 






