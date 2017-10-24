import odoo_client
import rdf_manager


def main():
    rdf_store = rdf_manager.RdfStore()

    hosts = [{'host': str(item['host']['value']),
              'host_uri': str(item['hostUri']['value'])} for item in list(rdf_store.get_hosts())]

    users = [{'user': str(item['user']['value']),
              'user_uri': str(item['userUri']['value']),
              'host_uri': str(item['hostUri']['value'])} for item in list(rdf_store.get_users())]

    keys = [{'label': str(item['label']['value']),
             'key_hash': str(item['keyHash']['value']),
             'key_type': str(item['keyType']['value']),
             'key_uri': str(item['keyUri']['value']),
             'user_uri': str(item['userUri']['value'])} for item in list(rdf_store.get_keys())]

    odoo_proxy = odoo_client.OdooProxy()
    odoo_proxy.import_hosts(hosts)
    odoo_proxy.import_users(users)
    odoo_proxy.import_keys(keys)

if __name__ == '__main__':
    main()