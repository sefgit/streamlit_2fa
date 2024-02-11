import os
import json
import streamlit as st

def load(sid):
    filename = f"{sid}.json"
    try:
        path = os.path.join("sessions", filename)
        with open(path, "r") as f:
            states = json.load(f)
            for a in states:
                st.session_state[a] = states[a]
    except Exception as e:
        st.error(e)

def save(sid, states):
    filename = f"{sid}.json"
    try:
        path = os.path.join("sessions", filename)
        with open(path, "w") as f:
            json.dump(states, f)
    except Exception as e:
        st.error(e)

def delete(sid):
    filename = f"{sid}.json"
    try:
        path = os.path.join("sessions", filename)
        os.unlink(path)
    except Exception as e:
        st.error(e)

def update(sid, new_states):
    filename = f"{sid}.json"
    try:
        path = os.path.join("sessions", filename)
        states = None
        with open(path, "r") as f:
            states = json.load(f)
            for a in new_states:
                states[a] = new_states[a]
                st.session_state[a] = states[a]
        with open(path, "w") as f:
            json.dump(states, f)
    except Exception as e:
        st.error(e)

