import redis, json, ast
from utils import Singleton, generate_keys_counter, generate_keys_clerk, how_many_seconds_until_midnight
import firestore_ops
from datetime import datetime, timedelta
from dateutil.parser import parse

fs_ops = firestore_ops.Firestore()

class Redis(metaclass=Singleton):

    def __init__(self):
        self.redis_client = redis.Redis()
    
    def create_template_date(self, branch_id, date):
        # create hash name
        name = "{}/counter/{}".format(branch_id, date)
        
        # create a copy of template for the particular date
        self.redis_client.hmset(name, self.redis_client.hgetall("{}/counter/template".format(branch_id)))
        self.redis_client.expire(name, how_many_seconds_until_midnight())

    def update_template_counters(self, branch_id, date):
        # get all the requests for that date
        req = fs_ops.get_all_requests_for_day(branch_id, date)
        
        traffic = len(req)
        pending = 0
        served = 0
        apt = 0

        # update the corresponding counters based on counter_id, slot_id and req_mode
        template_name = "{}/counter/{}".format(branch_id, date)

        if not self.check_key_exists(template_name):
            self.create_template_date(branch_id, date)

        for r in req:
            if not r['allotted']:
                continue
            if r['req_type'] == "online":
                self.redis_client.hincrby(template_name, "{}/slot/{}/NONCUR".format(r['counter_id'], r['slot_id']), 1)
            else:
                self.redis_client.hincrby(template_name, "{}/slot/{}/NOFFCUR".format(r['counter_id'], r['slot_id']), 1)
            
            if r['status'] == 'pending':
                pending += 1
            else:
                served += 1
                apt += int(r['processing_time'])
            
        if served > 0:
            apt /= served

        # set the keys of the dashboard
        if self.redis_client.hsetnx("traffic", branch_id, traffic):
            self.redis_client.expire("traffic", how_many_seconds_until_midnight())
        
        if self.redis_client.hsetnx("pending", branch_id, pending):
            self.redis_client.expire("pending", how_many_seconds_until_midnight())

        if self.redis_client.hsetnx("served", branch_id, served):
            self.redis_client.expire("served", how_many_seconds_until_midnight())

        if self.redis_client.hsetnx("apt", branch_id, apt):
            self.redis_client.expire("apt", how_many_seconds_until_midnight())

    def load_branch(self, branch_id):
        flag = self.check_key_exists("{}".format(branch_id))
        
        if flag:
            return True
        
        branch = fs_ops.load_branch(branch_id)
        
        if not branch:
            return False
        
        try:
            # get the counter keys for counter
            custom_counter_keys = generate_keys_counter(branch['counter'])

            # get the keys for clerk
            custom_clerk_keys = generate_keys_clerk(branch_id, branch['clerk'])

            # counter template
            custom_counter_key_name = "{}/counter/template".format(branch_id)

            # set the branch info
            self.redis_client.hset(branch_id, "info", json.dumps(branch["info"]))

            # set the counter template
            self.redis_client.hmset(custom_counter_key_name, custom_counter_keys)

            # set the clerk keys
            for k, v in custom_clerk_keys.items():
                self.redis_client.set(k, v)

            # set the counter info
            self.redis_client.hset(branch_id, "counter", json.dumps(branch["counter"]))

            # set clerk info
            self.redis_client.hset(branch_id, "clerk", json.dumps(branch["clerk"]))

            # create template for today
            # self.create_template_date(branch_id, str(datetime.now().date()))

            # update the template for the day
            # self.update_template_counters(branch_id, str(datetime.now().date()))
        except Exception as e:
            print(e)
            # print('Empty counter and clerk')
            # pass

    def incr_hash(self, hash_name, hash_key, incr_val):
        self.redis_client.hincrby(hash_name, hash_key, incr_val)

    def check_hash_key_exists(self, hash_name, hash_key):
        if self.redis_client.hexists(hash_name, hash_key):
            return True
        return False

    def check_key_exists(self, key):
        if self.redis_client.exists(key):
            return True
        return False

    def list_counter(self, branch_id):
        return self.redis_client.hget(branch_id, "counter")

    def list_clerk(self, branch_id):
        return self.redis_client.hgetall(branch_id)

    def add_counter(self, branch_id, counter_info):
        _, value = self.redis_client.hscan("{}/counter/template".format(branch_id), 0, "{}/*".format(counter_info['id'].strip()))

        if value:
            return False, "Counter ID already taken. Choose a different ID and re-enter the details"

        counter_info['slots'] = ast.literal_eval(counter_info['slots'].replace("null", "None"))
        counters = self.list_counter(branch_id)
        counters = json.loads(counters)
        n = int(counter_info['N'])
        non = int(n * int(counter_info['Nonline'])/100)
        noff = int(n * int(counter_info['Noffline'])/100)
        counters[counter_info['id']] = {"type":counter_info['type'], "N":n, "Nonline":non, "Noffline":noff, "TTL":counter_info['ttl'],"slots":{}}
        for s in counter_info['slots']:
            counters[counter_info['id']]['slots'][s[0]] = "{}_{}".format(s[1], s[2])
        self.redis_client.hset(branch_id, "counter", json.dumps(counters))

        # add to counter template
        counter_keys = generate_keys_counter({counter_info['id'] : counters[counter_info['id']]})
        for k, v in counter_keys.items():
            self.redis_client.hset("{}/counter/template".format(branch_id), k, v)
        
        # add to date template
        value = self.redis_client.keys("{}/counter/[0-9]*".format(branch_id))

        for t in value:
            dt = parse(str(t).split('/')[-1])
            counter_ttl = parse(counter_info['ttl'])
            if dt <= counter_ttl:
                for k, v in counter_keys.items():
                    self.redis_client.hset(t, k, v)

        # add to firestore
        flag = fs_ops.add_counter(branch_id, {counter_info['id']:counters[counter_info['id']]})
        
        if flag:
            return True, "Counter Creation Successful"
        return False, "Counter Creation Failed. Please re-enter the details and retry again"
    
    def add_clerk(self, branch_id, clerk_info):
        _, value = self.redis_client.hscan("{}/counter/template".format(branch_id), 0, "{}/*".format(clerk_info['counter_id'].strip()))
        if not value:
            return False, "counter id not found."
        flag, uid = fs_ops.add_clerk(branch_id, clerk_info)
        if not flag:
            return flag, "Problem in creating User. Please contact Admin"
        self.redis_client.set("{}/clerk/{}".format(branch_id, uid), clerk_info['counter_id'])
        clerk_value = self.redis_client.hget(branch_id, "clerk")
        clerk_value = json.loads(clerk_value)
        clerk_value[uid] = {'counter_id':clerk_info['counter_id']}
        self.redis_client.hset(branch_id, "clerk", json.dumps(clerk_value))
        return True, "Clerk creation successful. Please verify the clerk mail"

    def remove_clerk(self, branch_id, clerk_id):
        flag = self.redis_client.get("{}/clerk/{}".format(branch_id, clerk_id))
        if not flag:
            return False, "clerk id not found."
        flag = fs_ops.remove_clerk(branch_id, clerk_id)
        if not flag:
            return flag, "Problem in removing User. Please contact Admin"
        self.redis_client.delete("{}/clerk/{}".format(branch_id, clerk_id))
        clerk_value = self.redis_client.hget(branch_id, "clerk")
        clerk_value = json.loads(clerk_value)
        del clerk_value[clerk_id]
        self.redis_client.hset(branch_id, "clerk", json.dumps(clerk_value))
        return True, "Clerk removal successful"
    
    def get_traffic(self, branch_id):
        return self.redis_client.hget("traffic", branch_id)

    def get_pending(self, branch_id):
        return self.redis_client.hget("pending", branch_id)

    def get_served(self, branch_id):
        return self.redis_client.hget("served", branch_id)
    
    def get_apt(self, branch_id):
        return self.redis_client.hget("apt", branch_id)
    
    def get_user_info(self, uid):
        info = fs_ops.get_user_info(uid)
        return {'mail':info.email, 'name':info.display_name}

    def allocate_request(self, req_info):
        branch_id = req_info['branch_id']
        counter_id = req_info['counter_id']
        slot_id = req_info['slot_id']
        on_off = req_info['type']
        req_date = req_info['req_date']
        usr_id = req_info['usr_id']

        # check if the counter template exists
        flag = self.check_key_exists(branch_id)
        flag_req = self.check_key_exists("{}/counter/{}".format(branch_id, req_date))

        if not flag:
            self.load_branch(branch_id)
            self.update_template_counters(branch_id, req_date)

        if not flag_req:
            self.update_template_counters(branch_id, req_date)

        template_to_check = "{}/counter/{}".format(branch_id, req_date)

        req_json = {'branch_id':branch_id, 'counter_id':counter_id, 'slot_id': slot_id, 'time_request': datetime.now(), 'req_type': on_off, 'status': 'pending', 'req_date':parse(req_date), 'user_id':usr_id}

        message = "Request Allotted Successful"

        if on_off == 'online':
            threshold = int(self.redis_client.hget(template_to_check, "{}/NONPH".format(counter_id)))
            curr = int(self.redis_client.hget(template_to_check, "{}/slot/{}/NONCUR".format(counter_id, slot_id)))
            if curr > threshold:
                req_json['allotted'] = False
                message = "Request Allotted UnSuccessful. Please try the next slot"
            else:
                req_json['allotted'] = True
        else:
            threshold = int(self.redis_client.hget(template_to_check, "{}/NOFFPH".format(counter_id)))
            curr = int(self.redis_client.hget(template_to_check, "{}/slot/{}/NOFFCUR".format(counter_id, slot_id)))
            if curr > threshold:
                req_json['allotted'] = False
                message = "Request Allotted UnSuccessful. Please try the next slot"
            else:
                req_json['allotted'] = True

        flag, req_id = fs_ops.create_request(req_json)
        if not flag:
            message = "Request Creation Failed"
            return False, message, None

        # update counters
        if req_date == str(datetime.now().date()):
            # update the counters
            self.redis_client.hincrby("traffic", branch_id, 1)
            if req_json['allotted']:
                self.redis_client.hincrby("pending", branch_id, 1)
                if on_off == 'online':
                    self.redis_client.hincrby(template_to_check, "{}/slot/{}/NONCUR".format(counter_id, slot_id), 1)
                elif on_off == 'offline':
                    self.redis_client.hincrby(template_to_check, "{}/slot/{}/NOFFCUR".format(counter_id, slot_id), 1)

        return req_json['allotted'], message, req_id

    def push_to_queue(self, que_name, list_to_push):
        for i in list_to_push:
            self.redis_client.rpush(que_name, json.dumps(i))
        self.redis_client.expire(que_name, how_many_seconds_until_midnight())

    def construct_queue(self, info):
        reqs = fs_ops.read_requests(info)
        try:
            for i in reqs:
                print(i)
                i['req_date'] = str(i['req_date'])
                i['time_request'] = str(i['time_request'])
        except Exception as e:
            print(e)
        return reqs

    def current_slot(self, branch_id, counter_id):
        cnt = self.redis_client.hget(branch_id, "counter")
        if cnt is None:
            return 0
        cnts_info = json.loads(cnt)
        counter_info = cnts_info[counter_id]
        curr_time = datetime.now().time()
        slot_id = None
        for k, v in counter_info['slots'].items():
            t1, t2 = v.split('_')
            t1_dt = datetime.strptime(t1, "%H:%M").time()
            t2_dt = datetime.strptime(t2, "%H:%M").time()
            if t1_dt < curr_time < t2_dt:
                return k

        return slot_id

    def first_request(self, branch_id, usr_id):
        _ = self.load_branch(branch_id)
        cnt_id = self.redis_client.get("{}/clerk/{}".format(branch_id, usr_id)).decode("utf-8")
        slot_id = self.current_slot(branch_id, cnt_id)
        q_name = "{}/{}/requests".format(branch_id, cnt_id)
        q_len = self.redis_client.llen(q_name)
        
        if cnt_id is None or cnt_id == "NA":
            return 0

        if slot_id is None and q_len == 0:
            return 1
        
        if not self.check_key_exists(q_name):
            pre_reqs = self.construct_queue({'branch_id':branch_id, 'counter_id': cnt_id, 'slot_id': slot_id, 'next':False, 'req_date':parse(str(datetime.now().date()))})
            if pre_reqs == []:
                return 2
            last_time = pre_reqs[-1]['time_request']
            try:
                self.redis_client.hmset(q_name+'/metadata', {'last_time':last_time, 'slot_id':slot_id})
                self.redis_client.expire(q_name+'/metadata', how_many_seconds_until_midnight())
                self.push_to_queue(q_name, pre_reqs)
            except Exception as e:
                print(e)
        
        front = self.redis_client.lpop("{}/{}/requests".format(branch_id, cnt_id))
        front = json.loads(front)
        # user_info = fs_ops.get_user_info(front['user_id'])
        # print(user_info)
        # front['name'] = user_info.display_name
        # front['mail'] = user_info.email
        front['name'] = front['user_id']
        front['mail'] = 'dummymail@gmail.com'
        front['number'] = '123456789'
        return front
    
    def counter_update(self, branch_id, p_time):
        self.incr_hash("pending", branch_id, -1)
        self.incr_hash("served", branch_id, 1)
        apt_val_new = self.get_apt(branch_id)
        if not self.get_served(branch_id):
            apt_val_new = (p_time + apt_val_new)/ self.get_served(branch_id)
        else:
            apt_val_new = p_time
        
        self.redis_client.hset("apt", branch_id, apt_val_new)

    def next_request(self, branch_id, usr_id, info):
        cnt_id = self.redis_client.get("{}/clerk/{}".format(branch_id, usr_id)).decode("utf-8")

        # first update the request
        info['clerk_id'] = usr_id
        fs_ops.update_request(info)
        self.counter_update(branch_id, info['processing_time'])

        if cnt_id is None or cnt_id == "NA":
            return 0

        q_name = "{}/{}/requests".format(branch_id, cnt_id)
        q_len = self.redis_client.llen(q_name)
        req_json = {'branch_id':branch_id, 'counter_id': cnt_id, 'next':True, 'req_date':parse(str(datetime.now().date()))}

        if q_len == 0:
            return 2

        if q_len <= 3:
            pres_slot = str(self.current_slot(branch_id, cnt_id))
            stored_slot = self.redis_client.hget(q_name+'/metadata', 'slot_id').decode('utf-8')
            if pres_slot == stored_slot:
                last_time = parse(self.redis_client.hget(q_name+'/metadata', 'last_time'))
                req_json['time_request'] = last_time
                req_json['slot_id'] = stored_slot
                new_reqs = self.construct_queue(req_json)
                self.push_to_queue(q_name, new_reqs)
            else:
                last_time = parse(self.redis_client.hget(q_name+'/metadata', 'last_time'))
                req_json['time_request'] = last_time
                req_json['slot_id'] = stored_slot
                pending_reqs = self.construct_queue(req_json)
                self.push_to_queue(q_name, pending_reqs)
                return self.first_request(branch_id, usr_id)
        
        
        front = self.redis_client.lpop("{}/{}/requests".format(branch_id, cnt_id))
        front = json.loads(front)
        front['name'] = front['user_id']
        front['mail'] = 'dummymail@gmail.com'
        front['number'] = '123456789'
        return front
        
    def served_request(self, req_info):
        pass

