import firebase_admin
from firebase_admin import auth
from firebase_admin.auth import AuthError
from utils import Singleton
from firebase_admin import firestore
from dateutil.parser import  parse
import config, datetime
import utils
import json

class Firestore(metaclass=Singleton):

    def __init__(self):
        cred = firebase_admin.credentials.Certificate(config.FIRESTORE_CREDENTIALS)
        firebase_admin.initialize_app(cred)
        self.db = firestore.client()
    
    def get_clerks(self, branch_id):
        temp = {}
        clerk_info = self.db.collection('branch').document(branch_id).collection('clerks').stream()
        for c in clerk_info:
            temp[c.id] = c.to_dict()
            # self.get_user_info(c.id)
        return temp

    def get_counters(self, branch_id):
        temp = {}
        counter_info = self.db.collection('branch').document(branch_id).collection('counters').stream()
        for c in counter_info:
            temp[c.id] = c.to_dict()
        return temp

    def get_branch_info(self, branch_id):
        brn_info = self.db.collection('branch').document(branch_id).get()
        brn_info = brn_info.to_dict()
        if brn_info is None:
            return False, None
        return True, brn_info

    def load_branch(self, branch_id):
        flag, brn_info = self.get_branch_info(branch_id)
        if not flag:
            return None
        branch = {'info':brn_info}
        counters = self.get_counters(branch_id)
        branch["counter"] = counters
        clerks = self.get_clerks(branch_id)
        branch["clerk"] = clerks
        return branch

    def add_counter(self, branch_id, counter_info):
        try:
            counter_name = list(counter_info.keys())[0]
            self.db.collection('branch').document(branch_id).collection('counters').document(counter_name).set({
                "N": counter_info[counter_name]['N'],
                "Nonline": counter_info[counter_name]['Nonline'],
                "Noffline": counter_info[counter_name]['Noffline'],
                "type": counter_info[counter_name]['type'],
                "TTL": counter_info[counter_name]['TTL'],
                "slots": counter_info[counter_name]['slots']
            })
            return True
        except Exception as e:
            print(e)
            return False

    def add_clerk(self, branch_id, clerk_info):
        name = clerk_info['clerk_name']
        email = clerk_info['clerk_mail']
        passwd = clerk_info['new_password']
        counter_id = clerk_info['counter_id']
        flag, uid = self.create_user(name, email, passwd, branch_id)
        if not flag:
            return False, "Cannot Add User to Authentication"
        try:
            self.db.collection('branch').document(branch_id).collection('clerks').document(uid).set({
                'counter_id':counter_id
            })
            return True, uid
        except:
            return False, None
    
    def create_user(self, name, mail, password, branch_id):
        try:
            user = auth.create_user(
                email=mail,
                email_verified=False,
                password=password,
                display_name=name)
            auth.set_custom_user_claims(user.uid, {'clerk': True, 'branch_id':branch_id})
            return True, user.uid
        except:
            return False, None

    def remove_clerk(self, branch_id, uid):
        flag = self.remove_user(uid)
        if not flag:
            return flag
        try:
            self.db.collection('branch').document(branch_id).collection('clerks').document(uid).delete()
            return True
        except:
            return False

    def get_all_requests_for_day(self, branch_id, date, counter_id=None):
        req = self.db.collection('request').where(u'branch_id', u'==', branch_id).where(u'req_date', u'==', parse(date))
        if counter_id is None:
            res = req.stream()
        else:
            res = req.where(u'counter_id', counter_id).stream()
        return [r.to_dict() for r in res]
    
    def get_user_info(self, uid):
        user = auth.get_user(uid)
        return user

    def remove_user(self, uid):
        try:
            auth.delete_user(uid)
            return True
        except:
            return False

    def create_request(self, req_info):
        try:
            req = self.db.collection('request').add(req_info)
            return True, req[1].id
        except Exception as e:
            print(e)
            return False, None

    def read_requests(self, info):
        try:
            res = self.db.collection('request').where(u'branch_id', u'==', info['branch_id']).where('counter_id', '==', info['counter_id']).where('slot_id', '==', info['slot_id']).where('allotted', '==', True).where('req_date', '==', info['req_date']).where('status','==','pending')
            if info['next']:
                res = res.where('time_request', '>', info['time_request'])
            res = res.order_by('time_request').stream()
        except Exception as e:
            print(e)
        temp = []
        for r in res:
            a = r.to_dict()
            a.update({'req_id':r.id})
            temp.append(a)
        return temp

    def update_request(self, info):
        try:
            self.db.collection('request').document(info['req_id']).update({'comments':info['comments'],'processing_time':info['processing_time'], 'status':'served', 'updated_time':datetime.datetime.now(), 'clerk_id':info['clerk_id']})
            return True
        except Exception as e:
            print(e)
            return False