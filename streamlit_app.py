import streamlit as st
from supabase import create_client
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# --- SUPABASE CONFIG ---
url = "https://btywlttteyipgtpiyifa.supabase.co"
key = "sb_publishable_KgSA8z2DpoteCNPfG-sIlw_A_-kRyqy"
supabase = create_client(url, key)

st.set_page_config(page_title="Personal Note", layout="centered")
st.title("Personal Note 📝")

# --- AUTO REFRESH REAL-TIME ---
st_autorefresh(interval=2000)

# --- PASSWORD PROTECTION ---
PASSWORD = "n+a"

if "unlocked" not in st.session_state:
    st.session_state.unlocked = False

# If not unlocked, show password input
if not st.session_state.unlocked:
    pwd = st.text_input("Enter password", type="password")
    if pwd == PASSWORD:
        st.session_state.unlocked = True
        st.success("Unlocked! Remembered for this session.")
    else:
        st.stop()

# --- ROOM / NOTEBOOK ---
room = st.text_input("Notebook name", "personal")
if not room:
    st.stop()

st.divider()

# --- WRITE NOTE ---
note = st.text_area("Write note")

if st.button("Save"):
    if note:
        supabase.table("vault").insert({
            "room": room,
            "content": note,
            "created_at": str(datetime.utcnow())
        }).execute()
        st.success("Saved")

# --- VIEW MESSAGES (One-time, auto-delete after 5 minutes) ---
if "viewed_messages" not in st.session_state:
    st.session_state.viewed_messages = {}

if st.button("👁️ View messages"):
    data = supabase.table("vault").select("*").eq("room", room).order("created_at").execute()
    now = datetime.utcnow()
    for n in data.data:
        st.write("• " + n["content"])
        # Save deletion time (5 minutes later)
        st.session_state.viewed_messages[n["id"]] = now + timedelta(minutes=5)
    
# Auto-delete messages 5 minutes after viewing
for msg_id, delete_time in list(st.session_state.viewed_messages.items()):
    if datetime.utcnow() >= delete_time:
        supabase.table("vault").delete().eq("id", msg_id).execute()
        del st.session_state.viewed_messages[msg_id]

# --- CLEAR ALL ---
if st.button("🧹 Clear all"):
    supabase.table("vault").delete().eq("room", room).execute()
    st.warning("All notes deleted")
