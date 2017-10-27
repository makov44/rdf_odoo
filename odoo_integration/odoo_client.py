import xmlrpc.client


class OdooProxy():
    uid = -1
    models = None
    db = 'odoo11'
    password = 'admin'
    user = 'admin'

    def __init__(self):
        base_url = 'http://localhost:8069'
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(base_url))
        self.models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(base_url))
        self.uid = common.authenticate(self.db, self.user, self.password, {})

    def import_hosts(self, hosts):
        try:
            for host in hosts:
                host_uris = self.models.execute_kw(self.db, self.uid, self.password,
                                                   'audit_ssh_keys.host', 'search', [[['uri', '=', host['host_uri']]]])
                if any(host_uris):
                    continue

                self.models.execute_kw(self.db, self.uid, self.password, 'audit_ssh_keys.host', 'create', [{
                    'name': host['host'], 'uri': host['host_uri']
                }])
        except Exception as e:
            print(e)

    def import_users(self, users):
        try:
            for user in users:
                host_ids = self.models.execute_kw(self.db, self.uid, self.password,
                                                  'audit_ssh_keys.host', 'search', [[['uri', '=', user['host_uri']]]])

                if len(host_ids) != 1:
                    raise Exception('Host uri %s doesn\'t exist or is not unique', user['host_uri'])

                user_ids = self.models.execute_kw(self.db, self.uid, self.password,
                                                  'audit_ssh_keys.user', 'search', [[['uri', '=', user['user_uri']]]])
                if any(user_ids):
                    continue

                self.models.execute_kw(self.db, self.uid, self.password, 'audit_ssh_keys.user', 'create', [{
                    'name': user['user'], 'uri': user['user_uri'], 'host_id': host_ids[0]
                }])
        except Exception as e:
            print(e)

    def import_keys(self, keys):
        try:
            for key in keys:
                user_ids = self.models.execute_kw(self.db, self.uid, self.password,
                                                  'audit_ssh_keys.user', 'search', [[['uri', '=', key['user_uri']]]])
                if len(user_ids) != 1:
                    raise Exception('User uri %s doesn\'t exist or is not unique', key['user_uri'])

                key_ids = self.models.execute_kw(self.db, self.uid, self.password,
                                                 'audit_ssh_keys.key', 'search', [[['uri', '=', key['key_uri']]]])
                if any(key_ids):
                    continue

                self.models.execute_kw(self.db, self.uid, self.password, 'audit_ssh_keys.key', 'create', [{
                    'label': key['label'], 'key_hash': key['key_hash'], 'key_type': key['key_type'], 'uri': key['key_uri'],
                    'user_id': user_ids[0]
                }])

        except Exception as e:
            print(e)
