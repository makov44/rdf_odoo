import odoo_client
import rdf_manager


def main():
    rdf_store = rdf_manager.RdfStore()
    hosts = [{'host': str(item[0]),
              'host_uri': str(item[1])} for item in rdf_store.get_hosts()]

    users = [{'user': str(item[0]),
              'user_uri': str(item[1]),
              'host_uri': str(item[2])} for item in rdf_store.get_users()]

    # keys = [{'label': str(item[0]),
    #          'key_hash': str(item[1]),
    #          'key_type': str(item[2]),
    #          'key_uri': str(item[3]),
    #          'user_uri': str(item[4])}
    #         for item in rdf_store.get_keys()]

    odoo_proxy = odoo_client.OdooProxy()
    odoo_proxy.import_hosts(hosts)
    odoo_proxy.import_users(users)
    #odoo_proxy.import_keys(keys)

if __name__ == '__main__':
    main()