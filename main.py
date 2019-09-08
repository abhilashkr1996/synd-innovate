from flask import Flask, render_template, request, jsonify, redirect, g, url_for
from firebase_admin import auth
import time, datetime
from db import authorize
from app import app_ops


app_operations = app_ops.AppOps()

app = Flask(__name__)

@app.route('/sessionLogin', methods=['POST'])
def session_login():
    try:
        id_token = request.json['idToken']
        decoded_claims = auth.verify_id_token(id_token)
        if time.time() - decoded_claims['auth_time'] < 5 * 60:
            expires_in = datetime.timedelta(days=5)
            expires = datetime.datetime.now() + expires_in
            session_cookie = auth.create_session_cookie(id_token, expires_in=expires_in)
            response = app.make_response(jsonify({'status': 'success'}))
            response.set_cookie(
                'unique-key', session_cookie, expires=expires, httponly=True)
            return response
        return jsonify({'message':'Need to Re-SignIn'}), 401
    except ValueError as ve:
        return jsonify({'message':'Invalid ID token'}), 401
    except auth.AuthError as ae:
        return jsonify({'message':'Failed to create a session cookie'}), 401
    
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")

@app.route('/dashboard', methods=['POST','GET'])
@authorize.authorize
def dashboard():
    if 'clerk' in g.user and g.user['clerk']:
        return redirect(url_for("next_request"))
    if 'admin' in g.user and g.user['admin']:
        app_operations.login_checks(g.user['branch_id'])
        return render_template('admin/admin_dashboard.html', user="Admin")
    return render_template('404.html')

@app.route("/")
@app.route("/login")
def home():
    return render_template('login.html')

@app.route("/admin_clerk", methods=['GET'])
@authorize.authorize
@authorize.verify_admin
def admin_clerk():
    clerks_list = app_operations.list_all_clerks(g.user['branch_id'])
    return render_template('admin/admin_clerk.html', user="Abhilash", clerks=clerks_list)

@app.route("/add_clerk", methods=["POST"])
@authorize.authorize
@authorize.verify_admin
def add_clerk():
    _, msg = app_operations.add_clerk(g.user['branch_id'], request.form)
    clerks_list = app_operations.list_all_clerks(g.user['branch_id'])
    return render_template('admin/admin_clerk.html', user="Abhilash", clerks=clerks_list, server_msg=msg)

@app.route("/remove_clerk", methods=["POST"])
@authorize.authorize
@authorize.verify_admin
def remove_clerk():
    _, msg = app_operations.remove_clerk(g.user['branch_id'], request.form['uid'])
    clerks_list = app_operations.list_all_clerks(g.user['branch_id'])
    return render_template('admin/admin_clerk.html', user="Abhilash", clerks=clerks_list, server_msg_remove=msg)

@app.route("/admin_counter")
@authorize.authorize
@authorize.verify_admin
def admin_counter():
    counter_list = app_operations.list_all_counters(g.user['branch_id'])
    return render_template('admin/admin_counter.html', user="Abhilash", counters=counter_list)

@app.route("/admin_add_counter", methods=["POST"])
@authorize.authorize
@authorize.verify_admin
def admin_add_counter():
    _, msg = app_operations.add_counter(g.user['branch_id'], request.form.to_dict())
    counter_list = app_operations.list_all_counters(g.user['branch_id'])
    return render_template('admin/admin_counter.html', user="Abhilash", counters=counter_list, msg=msg)

@app.route("/get_traffic",methods=["GET"])
@authorize.authorize
@authorize.verify_admin
def get_traffic():
    n = app_operations.get_value_traffic(g.user['branch_id'])
    return jsonify({'value':(int(time.time())*1000,int(n))}), 200

@app.route("/tab_values", methods=["GET"])
@authorize.authorize
@authorize.verify_admin
def tab_values():
    pending_n = app_operations.get_value_pending(g.user['branch_id'])
    served_n = app_operations.get_value_served(g.user['branch_id'])
    apt_n = app_operations.get_value_apt(g.user['branch_id'])
    data = {'pending':pending_n.decode('utf-8'), 'served':served_n.decode('utf-8'), 'turntime':apt_n.decode('utf-8')}
    return jsonify(data), 200

@app.route("/system_dynamics")
@authorize.authorize
@authorize.verify_admin
def system_dynamics():
    return render_template("admin/system_dynamics.html")

###############
# clerk


@app.route("/clerk/dashboard", methods=["GET"])
def clerk_dashboard():
    return redirect(url_for('next_request'))

@app.route('/next_request', methods=['POST', 'GET'])
@authorize.authorize
@authorize.verify_clerk
def next_request():
    customer = app_operations.queue_request(g.user['branch_id'], g.user['user_id'], request.form.to_dict())
    print(customer)
    if isinstance(customer, dict):
        return render_template('clerk/clerk_dashboard.html', user="Abhilash", customer=customer)
    msg = ""
    if customer == 0:
        msg = "Counter Assigned is revoked or removed. Please contact Admin"
    elif customer == 1:
        msg = "No Slot for the current time - {}".format(datetime.datetime.now())
    elif customer == 2:
        msg = "No more pending requests. Click Refresh Button for more requests"
    
    return render_template("clerk/error.html", user="clerk", msg = msg)
    

@app.route("/request/pending", methods=["GET"])
def clerk_pending_request():
    return render_template('clerk/clerk_pending_request.html', user="Abhilash")

@app.route("/request/served", methods=["GET"])
def clerk_served_request():
    return render_template('clerk/clerk_done_request.html', user="Abhilash")

@app.route("/allocate/request")
def user_request():
    return render_template('request.html')

###############


@app.route("/allocate_request", methods=['POST'])
def allocate_request():
    status, msg, req_id = app_operations.allocate_request(request.form.to_dict())
    return jsonify({'status': status, 'message': msg, 'request_id': req_id}), 200

@app.route("/get_branch_info")
def branch_info():
    pass

if __name__ == '__main__':
    app.run(debug=True, use_debugger=True)