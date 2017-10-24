from SPARQLWrapper import SPARQLWrapper, JSON


class RdfStore:

    def __init__(self):
        self.sparql = SPARQLWrapper("http://rdf.getdyl.com:8890/sparql")

    def get_hosts(self):
        self.sparql.setQuery("""
        PREFIX ns1: <http://rdf.siliconbeach.io/schema/sys/v1/>
        SELECT DISTINCT ?host ?hostUri
        WHERE { 
        ?hostUri a ns1:system_instance;
                 ns1:system_instance.hostname ?host .
        }
        """)

        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()
        return results["results"]["bindings"]

    def get_users(self):
        self.sparql.setQuery("""
                PREFIX ns1: <http://rdf.siliconbeach.io/schema/sys/v1/>
                SELECT DISTINCT ?user ?userUri ?hostUri
                WHERE {
                ?hostUri a ns1:system_instance .
                ?userUri a ns1:user;
                     ns1:user.login ?user;
                     ns1:user.system ?hostUri .
                }
                """)

        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()
        return results["results"]["bindings"]

    def get_keys(self):
        self.sparql.setQuery("""
                PREFIX ns1: <http://rdf.siliconbeach.io/schema/sys/v1/>
                SELECT DISTINCT ?label ?keyHash ?keyType ?keyUri ?userUri
                WHERE { 
                ?userUri a ns1:user .                       
                ?keyUri a ns1:ssh_key;
                        ns1:ssh_key.key_type ?keyType;
                        ns1:ssh_key.public_sha1 ?keyHash .
                 ?authUri a ns1:authorized_key;
                        ns1:authorized_key.user  ?userUri;
                        ns1:authorized_key.ssh_key ?keyUri;
                        ns1:authorized_key.label ?label  .                      
                }
                """)
        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()
        return results["results"]["bindings"]