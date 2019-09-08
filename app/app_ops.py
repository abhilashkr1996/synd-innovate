from db import firestore_ops, redis_ops
import ast, datetime, json, dateutil

class AppOps:

    def __init__(self):
        self.cache = redis_ops.Redis()

    def add_counter(self, branch_id, counter_info):
        return self.cache.add_counter(branch_id, counter_info)
        
    def login_checks(self, branch_id):
        if not self.cache.check_key_exists("{}".format(branch_id)):
            self.cache.load_branch(branch_id)
        
        for k in ("traffic", "pending", "apt", "served"):
            flag = self.cache.check_hash_key_exists(k, branch_id)

            if not flag:
                self.cache.create_template_date(branch_id, str(datetime.datetime.now().date()))
                try:
                    self.cache.update_template_counters(branch_id, str(datetime.datetime.now().date()))
                except Exception as e:
                    print(e)
                return

    def list_all_counters(self, branch_id):
        counters = json.loads(self.cache.list_counter(branch_id))
        temp = []
        for c in counters:
            counters[c]['id'] = c
            temp.append(counters[c])
        return temp

    def list_all_clerks(self, branch_id):
        clerks = self.cache.list_clerk(branch_id)
        clerks = json.loads(clerks[b'clerk'])
        temp = []
        for k, v in clerks.items():
            temp_c = {}
            clerk_info = self.cache.get_user_info(k)
            temp_c['clerk_id'] = k
            temp_c['name'] = clerk_info.get('name')
            temp_c['email'] = clerk_info.get('mail')
            temp_c['counter_id'] = v['counter_id']
            temp.append(temp_c)
        return temp

    def add_clerk(self, branch_id, clerk_info):
        flag, msg = self.cache.add_clerk(branch_id, clerk_info)
        return flag, msg

    def remove_clerk(self, branch_id, clerk_id):
        return self.cache.remove_clerk(branch_id, clerk_id)

    def get_value_traffic(self, branch_id):
        return self.cache.get_traffic(branch_id)

    def get_value_pending(self, branch_id):
        return self.cache.get_pending(branch_id)
    
    def get_value_served(self, branch_id):
        return self.cache.get_served(branch_id)

    def get_value_apt(self, branch_id):
        return self.cache.get_apt(branch_id)

    def allocate_request(self, req_info):
        return self.cache.allocate_request(req_info)

    def queue_request(self, branch_id, usr_id, info):
        print(info)
        try:
            if info:
                return self.cache.next_request(branch_id, usr_id, info)
            return self.cache.first_request(branch_id, usr_id)
        except Exception as e:
            print(e)

    def send_branch_info(self, branch_id):
        pass