import streamlit as st
from hpc_manager import RemoteProjectFileSystem

@st.cache_resource
def get_fs(host: str, username: str, password: str, protocol: str):
    fs = RemoteProjectFileSystem(host, username, password, protocol)
    return fs