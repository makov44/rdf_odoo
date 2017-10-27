import odoo_client
import rdf_manager

host_query = """
        PREFIX ns1: <http://rdf.siliconbeach.io/schema/sys/v1/>
        SELECT DISTINCT ?host ?hostUri
        WHERE { 
        ?hostUri a ns1:system_instance;
                 ns1:system_instance.hostname ?host .
        }
        """

user_query = """
                PREFIX ns1: <http://rdf.siliconbeach.io/schema/sys/v1/>
                SELECT DISTINCT ?user ?userUri ?hostUri
                WHERE {
                ?hostUri a ns1:system_instance .
                ?userUri a ns1:user;
                     ns1:user.login ?user;
                     ns1:user.system ?hostUri .
                }
                """

key_query = """
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
                """


def main():
    rdf_store = rdf_manager.RdfStore()

    hosts = rdf_store.execute(host_query)

    users = rdf_store.execute(user_query)

    keys = rdf_store.execute(key_query)

    odoo_proxy = odoo_client.OdooProxy()
    odoo_proxy.import_hosts(hosts)
    odoo_proxy.import_users(users)
    odoo_proxy.import_keys(keys)

if __name__ == '__main__':
    main()