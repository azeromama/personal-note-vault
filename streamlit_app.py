import streamlit as st
from supabase import create_client, Client
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# ---------------- Supabase Setup ----------------
url = "https://btywlttteyipgtpiyifa.supabase.co"
key = "sb_publishable_KgSA8z2DpoteCNPfG-sIlw_A_-kRyqy"
supabase: Client = create_client(url, key)

# ---------------- Streamlit UI ----------------
st.set_page_config(page_title="💬 Secret Chat", page_icon="🔐")
st.title("💬 Secret Chat")
st_autorefresh(interval=2000, key="refresh")  # real-time update

# ---------------- Password ----------------
if "unlocked" not in st.session_state:
    st.session_state.unlocked = False

password = st.text_input("Enter password:", type="password")
if st.button("Unlock"):
    if password == "n+a":  # example password
        st.session_state.unlocked = True
        st.success("Unlocked ✅")
    else:
        st.error("Wrong password ❌")

if not st.session_state.unlocked:
    st.stop()

# ---------------- Chat Room ----------------
chat_id = st.text_input("Enter chat ID (share with your friend):")
if not chat_id:
    st.info("Enter a chat ID to start chatting")
    st.stop()

# ---------------- Message Input ----------------
message = st.chat_input("Type your message...")
if message:
    supabase.table("messages").insert({
        "chat_id": chat_id,
        "text": message,
        "created_at": datetime.utcnow(),
        "sender": "me",
        "seen_at": None
    }).execute()

# ---------------- Display Messages ----------------
now = datetime.utcnow()
msgs = supabase.table("messages").select("*").eq("chat_id", chat_id).order("created_at").execute().data
to_delete = []

for msg in msgs:
    # Auto-delete if viewed >5 min
    if msg.get("seen_at") and (now - msg["seen_at"]).total_seconds() > 300:
        to_delete.append(msg["id"])
        continue
    
    with st.chat_message("Friend" if msg["sender"] != "me" else "You"):
        st.write(msg["text"])
    
    # Mark as seen
    if not msg.get("seen_at"):
        supabase.table("messages").update({"seen_at": datetime.utcnow()}).eq("id", msg["id"]).execute()

# Delete old messages
for msg_id in to_delete:
    supabase.table("messages").delete().eq("id", msg_id).execute()

# ---------------- Clear All ----------------
if st.button("🧹 Clear All Messages"):
    supabase.table("messages").delete().eq("chat_id", chat_id).execute()
    st.success("All messages cleared ✅")
