from functools import wraps
from flask import Flask, render_template, request, jsonify, redirect, g, url_for
from utils import Singleton
from firebase_admin import auth
from firebase_admin.auth import AuthError

def authorize(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        session_cookie = request.cookies.get('unique-key')
        try:
            g.user = auth.verify_session_cookie(session_cookie, check_revoked=True)
            return f(*args, **kwargs)
        except Exception as exp:
            return redirect('/login')
        
    return decorated_function

def verify_admin(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            if 'admin' not in g.user or not g.user['admin']:
                return jsonify({'message':'You are not authorised to perform the operation'}), 401
            return f(*args, **kwargs)
        except:
            return jsonify({'message':'Internal Server Error'}), 500

    return decorated_function

def verify_clerk(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            if 'clerk' not in g.user or not g.user['clerk']:
                return jsonify({'message':'You are not authorised to perform the operation'}), 401
            return f(*args, **kwargs)
        except:
            return jsonify({'message':'Internal Server Error'}), 500

    return decorated_function