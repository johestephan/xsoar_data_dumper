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

def datadump_to_couchdb(URLload, header, couchLINK):
    con = sqlite3.connect("DataDumper.db")
    cur = con.cursor()
    res = cur.execute("SELECT id FROM incidents WHERE fetched='ToDo'")
    couch = couchdb.Server(couchLINK)
    if not 'incidents' in couch:
        db = couch.create('incidents')
    db = couch['incidents']
    for incid in res.fetchall():
        dataset = requests.get(URLload+incid[0], headers=header, verify=False)
        JObject = json.loads(dataset.text)
        db.save(JObject)
        cur.execute("UPDATE incidents SET fetched = 'Done' WHERE id = '%s' " % incid[0])
        con.commit()


def datadump(URLload, header):
    con = sqlite3.connect("DataDumper.db")
    cur = con.cursor()
    res = cur.execute("SELECT id FROM incidents WHERE fetched='ToDo'")
    for incid in res.fetchall():
        dataset = requests.get(URLload+incid[0], headers=header, verify=False)
        JObject = json.loads(dataset.text)
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

    args = parser.parse_args()
    header = json.loads('''{"Authorization" : "%s", 
          "Content-Type": "application/json", 
          "Accept": "application/json"}''' % (args.auth))
    URLload = str(args.base) +"/incident/load/"
    URLsearch = str(args.base) + "/incidents/search"
    if args.init:
        createDB(URLsearch, header)
    elif args.run:
        if args.couchdb is not None:
            datadump_to_couchdb(URLload, header, args.couchdb)
        else:
            datadump(URLload, header) 






