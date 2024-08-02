from paramiko import SSHClient, AutoAddPolicy
from scp import SCPClient
import streamlit as st
from typing import Tuple

def create_scp_client(server_ip: str, username: str, password: str) -> Tuple[SCPClient, SSHClient]:
    ssh = SSHClient()
    ssh.set_missing_host_key_policy(AutoAddPolicy())
    ssh.connect(server_ip, username=username, password=password)
    return SCPClient(ssh.get_transport()), ssh

def login_dialog():
    """
    Sets the login information in streamlit session state
    """
    st.title("Login")
    server_ip = st.text_input("Server IP", value="login02.scripps.edu")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if username == "debug":
        st.session_state['authenticated'] = True
        st.session_state['server_ip'] = server_ip
        st.session_state['username'] = username
        st.session_state['password'] = password
        st.rerun()

    if st.button("Login", type="primary"):
        try:
            scp, ssh = create_scp_client(server_ip, username, password)
            scp.close()
            ssh.close()
            st.session_state['authenticated'] = True
            st.session_state['server_ip'] = server_ip
            st.session_state['username'] = username
            st.session_state['password'] = password
            st.success("Login successful!")
            st.rerun()
        except Exception as e:
            st.error(f"Login failed: {str(e)}")

def login():
    """
    Will stop streamlit execution if use is not logged in
    """
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False

    if not st.session_state['authenticated']:
        login_dialog()
        st.stop()