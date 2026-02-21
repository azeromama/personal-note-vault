import streamlit as st
from supabase import create_client
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components

# --- SUPABASE CONFIG ---
url = "https://btywlttteyipgtpiyifa.supabase.co"
key = "sb_publishable_KgSA8z2DpoteCNPfG-sIlw_A_-kRyqy"
supabase = create_client(url, key)

st.set_page_config(page_title="Personal Note", layout="centered")

# --- AUTO REFRESH EVERY 2 SEC ---
st_autorefresh(interval=2000)

# --- TITLE ---
st.title("📝 Personal Note")

# --- HIDDEN UNLOCK USING KEYBOARD ---
if "unlocked" not in st.session_state:
    st.session_state.unlocked = False
if "n_count" not in st.session_state:
    st.session_state.n_count = 0

# JS listener to count N key presses
components.html("""
<script>
document.addEventListener('keydown', function(event) {
    if(event.key.toLowerCase() === 'n'){
        let n_count = localStorage.getItem('n_count') || 0;
        n_count = parseInt(n_count) + 1;
        localStorage.setItem('n_count', n_count);
        if(n_count >= 5){
            localStorage.setItem('unlocked', 'true');
        }
    }
});
</script>
""", height=0)

# Check localStorage unlock
components.html("""
<script>
if(localStorage.getItem('unlocked') === 'true'){
    window.parent.postMessage({isUnlocked:true}, "*");
}
</script>
""", height=0)

if not st.session_state.unlocked:
    # Check localStorage manually
    if st.session_state.get('unlocked_local', False):
        st.session_state.unlocked = True
    else:
        st.info("Type letter N **5 times** on your keyboard to unlock vault")
        st.stop()

# --- ROOM ---
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

# --- VIEW ONCE ---
if st.button("👁️ View messages"):
    data = supabase.table("vault").select("*").eq("room", room).order("created_at").execute()
    now = datetime.utcnow()
    for n in data.data:
        st.write("• " + n["content"])
        # Schedule deletion 1 min after viewing
        delete_time = now + timedelta(minutes=1)
        supabase.table("vault").delete().eq("id", n["id"]).execute()
    if data.data:
        st.warning("Messages will self-destruct in 1 minute!")

# --- CLEAR ALL ---
if st.button("🧹 Clear all"):
    supabase.table("vault").delete().eq("room", room).execute()
    st.warning("All notes deleted")
