import re
import sys
import json
import hashlib
import glob
from pprint import pprint
from rdflib import plugin, Graph, Literal, URIRef, Namespace
from rdflib.store import Store
from rdflib.namespace import RDF, RDFS, XSD
from rdflib.serializer import Serializer
import rdflib_sqlalchemy

nsys = Namespace('http://rdf.siliconbeach.io/schema/sys/v1/')
dyl = Namespace('http://rdf.dyl.com/data/env/staging/')
hc = hashlib.sha1()


class RdfStore:

    def __init__(self):
        self.dburi = Literal('sqlite:///audit_rdf.db')
        self.ident = URIRef("http://rdf.siliconbeach.io/store/audit_rdf")
        rdflib_sqlalchemy.registerplugins()
        self.store = plugin.get("SQLAlchemy", Store)(identifier=self.ident)
        self.graph = Graph(self.store, identifier=self.ident)
        self.graph.open(self.dburi, create=True)
        self.build_graph('/Users/dyl/Downloads/audit')

    def get_hosts(self):
        return self.graph.query("""
        SELECT DISTINCT ?host ?hostUri
        WHERE { 
        ?hostUri a ns1:system_instance;
                 ns1:system_instance.hostname ?host .
        }
        """, initNs={'ns1': nsys})

    def get_users(self):
        return self.graph.query("""
                SELECT DISTINCT ?user ?userUri ?hostUri
                WHERE { 
                ?hostUri a ns1:system_instance .
                ?userUri a ns1:user;
                     ns1:user.login ?user;
                     ns1:user.system ?hostUri .                
                }              
                """, initNs={'ns1': nsys})

    def get_keys(self):
        return self.graph.query("""
                SELECT DISTINCT ?label ?keyHash ?keyType ?keyUri ?userUri
                WHERE { 
                ?userUri a ns1:user .                       
                ?keyUri a ns1:ssh_key;
                        ns1:ssh_key.key_type ?keyType;
                        ns1:ssh_key.public_sha1 ?keyHash;
                        ns1:ssh_key.label ?label;
                        ns1:ssh_key.user ?userUri .
                }              
                """, initNs={'ns1': nsys})

    def build_graph(self, data_source_path):
        crg = re.compile(r"^" + re.escape(data_source_path) + r"\/(.*)\.json")
        for filepath in glob.glob(data_source_path + '/*.json'):
            m = re.search(crg, filepath)
            host = m.group(1)
            hosturi = self.build_host(host)
            with open(filepath) as df:
                data = json.load(df)
                for user, ukeys in data.items():
                    useruri = self.build_user(hosturi, user)
                    for kdata in ukeys:
                        hc.update(kdata['public_key'].encode('utf-8'))
                        sh = hc.hexdigest()
                        self.build_key(useruri, kdata, sh)

    def build_host(self, host):
        hosturi = dyl['host/' + host]
        self.graph.add((hosturi, RDF.type, nsys['system_instance']))
        self.graph.add((hosturi, nsys['system_instance.hostname'], Literal(host)))
        return hosturi

    def build_user(self, hosturi, user):
        useruri = URIRef(str(hosturi) + '/user/' + user)
        self.graph.add((useruri, RDF.type, nsys['user']))
        self.graph.add((useruri, nsys['user.login'], Literal(user)))
        self.graph.add((useruri, nsys['user.system'], hosturi))
        return useruri

    def build_key(self, useruri, data, keyhash):
        keyuri = dyl['ssh_key/public_key_' + keyhash]
        self.graph.add((keyuri, RDF.type, nsys['ssh_key']))
        self.graph.add((keyuri, nsys['ssh_key.key_type'], Literal(data['type'])))
        self.graph.add((keyuri, nsys['ssh_key.public_sha1'], Literal(keyhash)))
        self.graph.add((keyuri, nsys['ssh_key.user'], useruri))
        if data['label']:
            self.graph.add((keyuri, nsys['ssh_key.label'], Literal(data['label'])))
        # authuri = URIRef(str(useruri) + '/authorized_key/' + keyhash)
        # self.graph.add((authuri, RDF.type, nsys['authorized_key']))
        # self.graph.add((authuri, nsys['authorized_key.user'], useruri))
        # self.graph.add((authuri, nsys['authorized_key.ssh_key'], keyuri))