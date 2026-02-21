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

# ---------- UNLOCK LOGIC ----------
if "unlocked" not in st.session_state:
    st.session_state.unlocked = False

if "n_count" not in st.session_state:
    st.session_state.n_count = 0

# Inject JS to listen for N key presses and store in localStorage
components.html("""
<script>
document.addEventListener('keydown', function(event) {
    if(event.key.toLowerCase() === 'n'){
        let count = parseInt(localStorage.getItem('n_count') || '0');
        count += 1;
        localStorage.setItem('n_count', count);
        if(count >= 5){
            localStorage.setItem('vault_unlocked', 'true');
            location.reload();
        }
    }
});
</script>
""", height=0)

# Check localStorage for unlock
components.html("""
<script>
if(localStorage.getItem('vault_unlocked') === 'true'){
    window.parent.postMessage({unlocked:true}, "*");
}
</script>
""", height=0)

# If not unlocked, show literally nothing
if not st.session_state.unlocked:
    # Try to detect via query (Streamlit can't read localStorage directly)
    st.stop()

# ---------- MAIN VAULT ----------
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
        # delete immediately after viewing, so you have 1 minute countdown (simulate)
        supabase.table("vault").delete().eq("id", n["id"]).execute()

# --- CLEAR ALL ---
if st.button("🧹 Clear all"):
    supabase.table("vault").delete().eq("room", room).execute()
    st.warning("All notes deleted")
