import firebase_admin
from firebase_admin import auth
from firebase_admin.auth import AuthError
from firebase_admin import firestore
import schedule, time


cred = firebase_admin.credentials.Certificate({
  "type": "service_account",
  "project_id": "synd-fa75d",
  "private_key_id": "9b3fda4b9dfd9275d817039e73ab484ed897715b",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC8fpfRttZ64uE8\nQcLgkaKXK7lSM7qqOusn5XuL6XmxIX2a6N2pAWdytURs1ptf7PU0XX7Dc/r9WPjN\nYzhnUs7jKlDIKaMSWBjx8ghCE+Ic77KSGQGuVYY+FiqjWwLYHFsbBvLF0KKVkJQ4\n9S9tMMbSOVM6SVPPBudaR/rXcnFtjpln3k5Ot3aWD7ciRHAFYSoCkckleAtBhZ9O\nGNOa67wSpZ48U9Rxf9XIcwOC9CqM38xkw/ZdA/AftZiz0pW8lBA3TqrzrVOyzt1I\nPoMM9bHo5VWIgZBK9X3YGS4P3mxE3YHNZTF7YBuZty0/NKhFvhOmE8cnpNBnRaBY\nDy/zWlx7AgMBAAECggEAAc2oQC5ioOxYwU3TwnhCOPYHIN0z1PsZUtlkNDN4oZQz\ncm715+8GgVdwnyXyeJl4wxZ95vrOFOxr/PMNEBf/uLan7TJQyBUlr/Lj11X/XM2C\nRNmOZY+V6DQoFkYBofWrfXe0jOXxGEM4186otH+59zrrK+yVq65iOj/kC3mh0i19\n20Shia66snJiWD9EXS7w5COL6qddf2wPAf/PUuZ6DNNjDNIN2lOUsYo8PCRoyhmz\nMwMivC38nA1mSmhxxxUy7zahSFUfsGEKyo+UWfvOHvHHMyrH3SL4Ly2KfHaO3EbL\nhDMpJiZjmX0F3636UTq9bW4gjr4+LhRk0iBmHb8+WQKBgQDxuTeAzWYrn2VvvZmW\na8Tv+A4Ac0urW9soGda6LMBhQmomThWb4iqlno1SAtSX9DkDPQTOWbu5vb3dPi8R\nRP5sBwPPgZQaC8rGU3uEhaYKxzSuErcmshE4wm3qZHsgMafl2375NqhlWCJ6wsDA\ncln2cXE4QkoVtVpQ06XiouopTQKBgQDHoJIPHMSvVPKhxtD65W2mnVJbmY+HLh1t\nyi0k+xytKklmspb0ODBu/dSjDlrNlzoOrsFNCe2oR9VLqmqwWPjZgbh8VCCQ0mek\ny8ft94cjWuRy0AgNW060FI5po5y8A9W+pue15V2U037o6R6S0Or9spI7P6sxyPUm\nebS8t/945wKBgQDvs8kLbCPeLFGtrinJFZOUl7pizfKCujMon/7kXg5kJDUZSSN6\nkpvR4tmnMvFYwjFrOa4zZp6XAUZvSAPqry1RON+ZfZi8/2aUpyJ8dwAB/isKV7rR\nn5EeZQgUgJHsifFCKhjOz1nMLcr7S3dTH9KAZVxt+qZ2woEOV+NPTFjCnQKBgDwc\nN57hVMBO3fiku0yxRQFEogX/CV71HdtvY4SdMJdcAlowMJA9Uyg4uoyWx/TcMpk1\nOfOOp8diSfHM0O9k+xnTm8+kLWIuWRMgYYVgYYrd1ahUx/ftpJdJEVDx+UIMDZKp\nA2CcPj+QJ8jOWWxwCDJ4UNwSYeRN1LPPNgMVjJHFAoGAHeU5DH4sTUjxX7OqzzZE\nqf6URl/hTkblvmUbhrPtcvcGFH4D6kbHQDIEStwUGKuwQuRZxLEO8UA02hbYNELB\n6Ou1snqVUDW76juEbVoYHak5nF8pJ+Bbd+079/AL0KAMPyK2yu/LNUc4xgesJp8/\nwa5lbQB94rs3zxPUNers+vY=\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-yqqe4@synd-fa75d.iam.gserviceaccount.com",
  "client_id": "103533255011207308404",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-yqqe4%40synd-fa75d.iam.gserviceaccount.com"
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