import streamlit as st
from supabase import create_client
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# ----------- Supabase Setup -----------
url = "https://btywlttteyipgtpiyifa.supabase.co"
key = "sb_publishable_KgSA8z2DpoteCNPfG-sIlw_A_-kRyqy"
supabase = create_client(url, key)

# ----------- UI Setup -----------
st.set_page_config(page_title="📝 Secret Note Chat", page_icon="🔐")
st.title("📝 Secret Note Chat")
st_autorefresh(interval=2000, key="refresh")  # refresh every 2 seconds

# ----------- Unlock with Note Name -----------
if "unlocked_note" not in st.session_state:
    st.session_state.unlocked_note = None

note_name = st.text_input("Enter your note name:", type="password")

if st.button("Unlock Note"):
    if note_name:
        st.session_state.unlocked_note = note_name
        st.success("Note unlocked ✅")
    else:
        st.error("Please enter a note name ❌")

if not st.session_state.unlocked_note:
    st.stop()

# ----------- Chat Room = Note Name -----------
chat_id = st.session_state.unlocked_note

# ----------- Message Input -----------
message = st.chat_input("Write a message to this note...")
if message:
    supabase.table("messages").insert({
        "chat_id": chat_id,
        "text": message,
        "created_at": datetime.utcnow(),
        "seen_at": None
    }).execute()

# ----------- Display Messages -----------
now = datetime.utcnow()
msgs = supabase.table("messages").select("*").eq("chat_id", chat_id).order("created_at").execute().data
to_delete = []

for msg in msgs:
    # Delete messages 5 min after reading
    if msg.get("seen_at") and (now - msg["seen_at"]).total_seconds() > 300:
        to_delete.append(msg["id"])
        continue
    with st.chat_message("📝 Note"):
        st.write(msg["text"])
    if not msg.get("seen_at"):
        supabase.table("messages").update({"seen_at": datetime.utcnow()}).eq("id", msg["id"]).execute()

# Delete old messages
for msg_id in to_delete:
    supabase.table("messages").delete().eq("id", msg_id).execute()

# ----------- Clear All -----------
if st.button("🧹 Clear All Messages"):
    supabase.table("messages").delete().eq("chat_id", chat_id).execute()
    st.success("All messages cleared ✅")
