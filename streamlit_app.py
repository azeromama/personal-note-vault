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

# --- AUTO REFRESH EVERY 2s ---
st_autorefresh(interval=2000)

# --- HIDDEN UNLOCK USING LOCAL STORAGE ---
if "unlocked" not in st.session_state:
    st.session_state.unlocked = False
if "tap" not in st.session_state:
    st.session_state.tap = 0

# Display title as "Personal Note"
components.html("""
<h1 id="title" style="cursor:pointer;">Personal Note</h1>
<script>
let tap = 0;
document.getElementById('title').addEventListener('click', function() {
    tap += 1;
    if (tap >= 3){
        localStorage.setItem('vault_unlocked','true');
        location.reload();
    }
});
</script>
""", height=50)

# Check local storage for unlock
components.html("""
<script>
if(localStorage.getItem('vault_unlocked') === 'true'){
    document.dispatchEvent(new Event('vaultUnlocked'));
}
</script>
""", height=0)

# Use st.session_state to remember unlock
if not st.session_state.unlocked:
    if 'vault_unlocked' not in st.session_state:
        st.stop()
    st.session_state.unlocked = True

st.success("Vault unlocked")

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

# --- VIEW ONE-TIME MESSAGES ---
if st.button("👁️ View messages"):
    data = supabase.table("vault") \
        .select("*") \
        .eq("room", room) \
        .order("created_at") \
        .execute()

    # Show messages
    for n in data.data:
        st.write("• " + n["content"])

    # Auto-delete 2 minutes after viewing
    if data.data:
        delete_time = datetime.utcnow() + timedelta(minutes=2)
        for n in data.data:
            supabase.table("vault").update({"created_at": delete_time}).eq("id", n["id"]).execute()
        # Streamlit won't auto-delete, so messages will vanish after 2 minutes in DB
        st.info("Messages will auto-delete in 2 minutes 💣")

# --- CLEAR ALL ---
if st.button("🧹 Clear all"):
    supabase.table("vault").delete().eq("room", room).execute()
    st.warning("All notes deleted")
