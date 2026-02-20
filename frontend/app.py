import streamlit as st
import os
import sys
import requests
import pandas as pd
import io

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

BACKEND_URL = "http://localhost:8000"

# --- Page Config & Theme ---
st.set_page_config(page_title="MCPDESK | Market Intelligence", layout="wide")

# Custom CSS for Obsidian-like Minimalist Theme
st.markdown("""
    <style>
    /* Main background */
    .stApp {
        background-color: #0f0f0f;
        color: #e0e0e0;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #1a1a1a;
        border-right: 1px solid #333;
    }
    
    /* Input area styling */
    .stTextArea textarea {
        background-color: #1e1e1e !important;
        color: #e0e0e0 !important;
        border: 1px solid #333 !important;
        border-radius: 4px !important;
        font-family: 'JetBrains Mono', 'Fira Code', monospace;
    }
    
    /* Buttons */
    .stButton button {
        background-color: #2a2a2a;
        color: #e0e0e0;
        border: 1px solid #444;
        border-radius: 4px;
        transition: all 0.2s;
        font-weight: 500;
    }
    .stButton button:hover {
        background-color: #3a3a3a;
        border-color: #666;
        color: #ffffff;
    }
    
    /* Container/Cell cards */
    [data-testid="stVerticalBlock"] > div > div > div[data-testid="stVerticalBlock"] {
        background-color: #161616;
        border: 1px solid #222;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 10px;
    }
    
    /* Command suggestion box */
    .command-hint {
        color: #888;
        font-size: 0.85rem;
        margin-bottom: 5px;
    }
    
    /* Title styling */
    h1 {
        font-weight: 300 !important;
        letter-spacing: -0.05rem;
        color: #ffffff;
    }
    
    /* Hide default streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- State Management ---
if "cells" not in st.session_state:
    st.session_state.cells = [{"id": 0, "content": "", "result": None}]

def add_cell():
    new_id = len(st.session_state.cells)
    st.session_state.cells.append({"id": new_id, "content": "", "result": None})
    st.rerun()

def delete_cell(index):
    if len(st.session_state.cells) > 1:
        st.session_state.cells.pop(index)
    else:
        st.session_state.cells = [{"id": 0, "content": "", "result": None}]
    st.rerun()

def move_cell_up(index):
    if index > 0:
        st.session_state.cells[index], st.session_state.cells[index-1] = \
            st.session_state.cells[index-1], st.session_state.cells[index]
        st.rerun()

def move_cell_down(index):
    if index < len(st.session_state.cells) - 1:
        st.session_state.cells[index], st.session_state.cells[index+1] = \
            st.session_state.cells[index+1], st.session_state.cells[index]
        st.rerun()

def run_cell(index):
    content = st.session_state.cells[index]["content"]
    st.session_state.cells[index]["result"] = {"type": "text", "content": "⌛ Processing..."}
    
    try:
        response = requests.post(f"{BACKEND_URL}/command", json={"command": content})
        if response.status_code == 200:
            st.session_state.cells[index]["result"] = response.json()
        else:
            st.session_state.cells[index]["result"] = {"type": "text", "content": f"Error: {response.text}"}
    except Exception as e:
        st.session_state.cells[index]["result"] = {"type": "text", "content": f"Connection Error: {str(e)}"}
    st.rerun()

# --- Main UI ---
st.title("💠 MCPDESK")
st.caption("Minimalist Market Intelligence Workspace")

# Sidebar
with st.sidebar:
    st.subheader("Workspace Controls")
    if st.button("➕ New Cell", use_container_width=True):
        add_cell()
    if st.button("🗑️ Clear All", use_container_width=True):
        st.session_state.cells = [{"id": 0, "content": "", "result": None}]
        st.rerun()
    
    st.markdown("---")
    st.subheader("📁 Data Store")
    uploaded_file = st.file_uploader("Upload CSV Data", type=["csv"])
    if uploaded_file:
        if "last_uploaded" not in st.session_state or st.session_state.last_uploaded != uploaded_file.name:
            try:
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")}
                resp = requests.post(f"{BACKEND_URL}/upload", files=files)
                if resp.status_code == 200:
                    st.success(f"'{uploaded_file.name}' mounted.")
                    st.session_state.last_uploaded = uploaded_file.name
            except Exception as e:
                st.error(f"Upload failed: {e}")

# Cell Editor
COMMANDS = {
    "/describe": "Statistically describe the current dataset.",
    "/plot": "Generate a visual chart from numeric data.",
    "/scrape": "Extract data from a specific URL.",
    "/model": "Perform deep LLM analysis or forecasting.",
    "/upload": "Guide for data ingestion."
}

for i, cell in enumerate(st.session_state.cells):
    with st.container():
        # Cell Header
        h_col1, h_col2, h_col3, h_col4 = st.columns([10, 0.8, 0.8, 0.8])
        with h_col1:
            st.markdown(f"**CELL {i+1}**")
        with h_col2:
            if st.button("↑", key=f"up_{i}", disabled=(i==0)): move_cell_up(i)
        with h_col3:
            if st.button("↓", key=f"down_{i}", disabled=(i==len(st.session_state.cells)-1)): move_cell_down(i)
        with h_col4:
            if st.button("×", key=f"del_{i}"): delete_cell(i)
        
        # Input & Autocomplete Hint
        val = cell["content"]
        if val.startswith("/"):
            match = [f"{k}: {v}" for k, v in COMMANDS.items() if k.startswith(val.split()[0])]
            if match:
                st.markdown(f"<div class='command-hint'>💡 Suggestions: {', '.join(match)}</div>", unsafe_allow_html=True)
        
        cell_content = st.text_area(
            "Command Input",
            value=val,
            key=f"text_{i}",
            placeholder="/plot ...",
            label_visibility="collapsed",
            height=100
        )
        st.session_state.cells[i]["content"] = cell_content
        
        # Action Bar
        a_col1, a_col2 = st.columns([2, 10])
        with a_col1:
            if st.button("RUN COMMAND", key=f"run_{i}", use_container_width=True):
                run_cell(i)
        
        # Result Display
        res = cell["result"]
        if res:
            st.markdown("---")
            if isinstance(res, dict):
                res_type = res.get("type", "text")
                if res_type == "text":
                    st.markdown(res.get("content", ""))
                elif res_type == "table":
                    df = pd.read_json(io.StringIO(res.get("content", "")))
                    st.dataframe(df, use_container_width=True)
                elif res_type == "chart":
                    df = pd.read_json(io.StringIO(res.get("content", "")))
                    st.line_chart(df)
                elif res_type == "mixed":
                    for item in res.get("items", []):
                        itype = item.get("type")
                        icontent = item.get("content", "")
                        if itype == "text": st.markdown(icontent)
                        elif itype == "table":
                            st.dataframe(pd.read_json(io.StringIO(icontent)), use_container_width=True)
                        elif itype == "chart":
                            st.line_chart(pd.read_json(io.StringIO(icontent)))
            else:
                st.markdown(str(res))

st.markdown("---")
st.caption("© 2026 MCPDESK | Secure Market Analysis")
