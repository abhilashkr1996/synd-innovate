import firebase_admin
from firebase_admin import auth
from firebase_admin.auth import AuthError
from firebase_admin import firestore
import schedule, time


cred = firebase_admin.credentials.Certificate({
})

firebase_admin.initialize_app(cred)
db = firestore.client()

def mail():
    pass


def generate_report():
    # for every branch, read all the requests for the day
    # yet to complete
    br = db.collection('branch').stream()
    br_res = [r.to_dict() for r in br]

    for branch in br_res:
      stats_temp = {}
      req = db.collection('request').where('branch_id','==', branch.id).stream()
      req_res = [r.to_dict() for r in br]
      traffic_n = len(req_res)
      pending_n = 0
      served_n = 0
      apt = 0
      pass


def remove_counters_less_than_today():
    pass

schedule.every().day.at("23:00").do(generate_report)
schedule.every().day.at("00:30").do(remove_counters_less_than_today)

while True:
    schedule.run_pending()
    time.sleep(2)
