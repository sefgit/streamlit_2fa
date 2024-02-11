import os
import json
import random
import time
import binascii
import string
import pickle
import requests
import streamlit as st
from streamlit_cookies_manager import CookieManager
from requests import Session, Response

import store

st.set_page_config(
    page_title="2FA",
    page_icon="👋",
)
page = st.empty()
cookies = CookieManager()

def logout():
    if 'authed' in st.session_state:
        if 'sid' in st.session_state:
            store.delete(st.session_state['sid'])

    with page.container(border=True):
        st.write(f"* state: {st.session_state['authed']}")
        st.write("# Logging out ! 👋")
        st.session_state['authed'] = False
        del st.session_state['username']
        if 'sid' in st.session_state:
            del st.session_state['sid']
        if 'req_session' in st.session_state:
            del st.session_state['req_session']
        if 'csrf_token' in st.session_state:
            del st.session_state['csrf_token']
        del cookies['sid']
        cookies.save()
        with st.spinner('...'):
            time.sleep(2)
        st.success('LOGOUT !')    
    time.sleep(2)
    st.rerun()
    
def authorized():
    with page.container(border=True):
        st.write(f"state: {st.session_state['authed']}")
        st.write("# Authenticated ! 👋")
        logout_btn = st.button("LOGOUT")
        if logout_btn:
            logout()
        
def authenticate_user():
    with page.container(border=True):
        username = st.session_state['username']
        otp = st.session_state['otp']
        st.write(f"# authenticate_user: '{username}':'{otp}'")
        #
        sid = st.session_state['sid'] # session id
        password = st.session_state['password']
        csrf_token = st.session_state['csrf_token']
        req_session = st.session_state['req_session']
        #
        # Is authentication successful ?
        #
        try:
            request_session = pickle.loads(binascii.unhexlify(req_session))
            st.write(type(request_session))
        except Exception as e:
            st.error(e)
        st.session_state['authed'] = True
        #
        # save our current states
        #
        states = {
            "username": username,
            "sid": sid,
            "authed": True,
            "csrf_token": csrf_token,
            "req_session" : req_session,
            "updated": int(time.time()),
        }
        store.save(sid, states)
        #
        del st.session_state['password']
        del st.session_state['otp']

        with st.spinner('...'):
            time.sleep(3)
        st.success('Authorized !')    

        cookies['sid'] = sid
        cookies.save()
        st.rerun()

def show_otp_form():
    with page.container(border=True):
        st.write("Please check your SMS / Authenticator app for your OTP code !")
        otp = st.text_input("OTP Code", value="")            
        #
        submit = st.button("SUBMIT", type="primary", key="otp_form")
        if submit:
            otp = otp.strip()
            if otp != "":            
                st.session_state['otp'] = otp
                authenticate_user()
                
def send_otp_request():
    csrf_token = "".join(random.choices(string.ascii_letters + string.digits, k=32))
    st.session_state['csrf_token'] = csrf_token
    request_session = requests.Session()
    req_session = pickle.dumps(request_session)
    st.session_state['req_session'] = str(binascii.hexlify(req_session), "ascii")
    # send OTP request
    # ...

def show_login_form():
    with page.container(border=True):
        username = st.text_input("Username/Email", value="")
        password = st.text_input("Password", value="", type="password")
        submit = st.button("SUBMIT", type="primary", key="login_form")
        if submit:
            username = username.strip()
            password = password.strip()
            if username != "" and password != "":
                st.session_state['username'] = username
                st.session_state['password'] = password
                # request OTP
                if 'csrf_token' not in st.session_state:
                    send_otp_request()
                show_otp_form()
                
def login():
    if 'username' not in st.session_state:
        show_login_form()
    elif 'otp' in st.session_state:
        authenticate_user()
    else:
        show_otp_form()
    
def main():
    
    # Get cookies
    if not cookies.ready():
        return

    # sid: session id
    if 'sid' in cookies:
        store.load(cookies['sid'])
    
    if 'sid' not in st.session_state:
        sid = str(binascii.hexlify(os.urandom(24)), 'ascii')
        st.session_state['sid'] = sid

    # Initialization
    if 'authed' not in st.session_state:
        st.session_state['authed'] = False

    if st.session_state['authed']:
        authorized()
    else:
        login()

    st.session_state
    st.write("Current cookies:", cookies)
    
if __name__ == "__main__":
    main()