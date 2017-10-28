import re
import sys
import json
import hashlib
import glob
from rdflib import plugin, Graph, Literal, URIRef, Namespace
from rdflib.store import Store
from rdflib.namespace import RDF, RDFS, XSD
from rdflib.serializer import Serializer

nsys = Namespace('http://rdf.siliconbeach.io/schema/sys/v1/')
dyl = Namespace('http://rdf.dyl.com/data/env/staging/')

hc = hashlib.sha1()

from SPARQLWrapper import SPARQLWrapper, JSON, BASIC


class RdfStore:

    def __init__(self):
        self.sparql = SPARQLWrapper("http://rdf.getdyl.com:8890/sparql")
        self.sparql.setHTTPAuth(BASIC)
        self.sparql.setCredentials('dba', 'dba')

    def execute(self, query):
        query_result = []
        self.sparql.method = 'POST'
        self.sparql.setQuery(query)
        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()
        for item in  results["results"]["bindings"]:
            dict_result={}
            for key in item:
                dict_result[key] = item[key]["value"]

            query_result.append(dict_result)

        return query_result


    def iterate_dir(self, base):
        crg = re.compile(r"^" + re.escape(base) + r"\/(.*)\.json")
        for filepath in glob.glob(base + '/*.json'):
            graph = Graph()
            m = re.search(crg, filepath)
            host = m.group(1)
            hosturi = self.build_host(host, graph)
            with open(filepath) as df:
                data = json.load(df)
                for user, ukeys in data.items():
                    useruri = self.build_user(hosturi, user, graph)
                    for kdata in ukeys:
                        self.build_key(useruri, kdata, graph)

            self.insert_nodes(graph)

    def insert_nodes(self, graph):
        result = graph.serialize(format='nt').decode("utf-8")
        hostInsert = """               
                       INSERT INTO <http://rdf.siliconbeach.io/store/audit_rdf>
                       {
                          %s
                       }            
                       """ % (result)
        self.execute(hostInsert)

    def build_host(self, host, graph):
        hosturi = dyl['host/' + host]
        hc.update(str(hosturi).encode('utf-8'))
        graph.add((hosturi, RDF.type, nsys['system_instance']))
        graph.add((hosturi, nsys['system_instance.hostname'], Literal(host)))
        graph.add((hosturi, nsys['system_instance.id'], Literal(int(hc.hexdigest()[:8], 16))))
        return hosturi

    def build_user(self, hosturi, user, graph):
        useruri = URIRef(str(hosturi) + '/user/' + user)
        hc.update(str(useruri).encode('utf-8'))
        graph.add((useruri, RDF.type, nsys['user']))
        graph.add((useruri, nsys['user.login'], Literal(user)))
        graph.add((useruri, nsys['user.system'], hosturi))
        graph.add((useruri, nsys['system_instance.id'], Literal(int(hc.hexdigest()[:8], 16))))
        return useruri

    def build_key(self, useruri, data, graph):
        hc.update(data['public_key'].encode('utf-8'))
        keyhash = hc.hexdigest()
        keyuri = dyl['ssh_key/public_key_' + keyhash]
        hc.update(str(keyuri).encode('utf-8'))
        graph.add((keyuri, RDF.type, nsys['ssh_key']))
        graph.add((keyuri, nsys['ssh_key.key_type'], Literal(data['type'])))
        graph.add((keyuri, nsys['ssh_key.public_sha1'], Literal(keyhash)))
        graph.add((keyuri, nsys['system_instance.id'], Literal(int(hc.hexdigest()[:8], 16))))
        authuri = URIRef(str(useruri) + '/authorized_key/' + keyhash)
        graph.add((authuri, RDF.type, nsys['authorized_key']))
        graph.add((authuri, nsys['authorized_key.user'], useruri))
        graph.add((authuri, nsys['authorized_key.ssh_key'], keyuri))
        try:
            graph.add((authuri, nsys['authorized_key.label'], Literal(data['label'])))
        except KeyError:
            pass
