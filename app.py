import streamlit as st
import sqlite3
from datetime import datetime
from pathlib import Path
import pandas as pd

DB_PATH = Path("atoz_powerwashing.db")
SERVICES = ["Driveway Cleaning", "Pressure Washing", "Siding Restoration", "Gutter Care"]

st.set_page_config(page_title="A to Z Power Washing | AI Communication", page_icon="💧", layout="wide")

st.markdown("""
<style>
.block-container {max-width: 1180px; padding-top: 2rem;}
.hero {padding: 1.5rem 1.7rem; border: 1px solid rgba(128,128,128,.25); border-radius: 18px; margin-bottom: 1rem;}
.hero h1 {margin: 0; font-size: 2rem;}
.muted {opacity: .72;}
[data-testid="stMetric"] {border: 1px solid rgba(128,128,128,.22); padding: 14px; border-radius: 14px;}
</style>
""", unsafe_allow_html=True)

def db():
    con = sqlite3.connect(DB_PATH, check_same_thread=False)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    con = db()
    con.executescript("""
    CREATE TABLE IF NOT EXISTS leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT,
        email TEXT,
        service TEXT NOT NULL,
        address TEXT NOT NULL,
        details TEXT,
        preferred_date TEXT,
        preferred_time TEXT,
        status TEXT NOT NULL DEFAULT 'New',
        created_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lead_id INTEGER,
        sender TEXT NOT NULL,
        message TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (lead_id) REFERENCES leads(id)
    );
    """)
    con.commit()
    con.close()

def save_message(sender, message, lead_id=None):
    con = db()
    con.execute("INSERT INTO messages (lead_id,sender,message,created_at) VALUES (?,?,?,?)",
                (lead_id, sender, message, datetime.now().isoformat(timespec="seconds")))
    con.commit()
    con.close()

def create_lead(name, phone, email, service, address, details, preferred_date, preferred_time):
    con = db()
    cur = con.execute("""INSERT INTO leads
        (name,phone,email,service,address,details,preferred_date,preferred_time,status,created_at)
        VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (name, phone, email, service, address, details, str(preferred_date),
         str(preferred_time), "New", datetime.now().isoformat(timespec="seconds")))
    lead_id = cur.lastrowid
    con.execute("INSERT INTO messages (lead_id,sender,message,created_at) VALUES (?,?,?,?)",
                (lead_id, "Customer", f"Quote request for {service}: {details}",
                 datetime.now().isoformat(timespec="seconds")))
    con.commit()
    con.close()
    return lead_id

def assistant_reply(message):
    text = message.lower()
    if any(word in text for word in ["emergency", "injury", "damage", "complaint", "human", "person"]):
        return "I’ll leave this for a team member rather than guess. Please use Quote & Scheduling to leave your contact information."
    if any(word in text for word in ["price", "cost", "quote", "estimate", "how much"]):
        return "Pricing depends on the service and property details. Open Quote & Scheduling and I can collect what the team needs for an estimate."
    if any(word in text for word in ["service", "offer", "do you clean"]):
        return "A to Z offers driveway cleaning, pressure washing, siding restoration, and gutter care."
    if any(word in text for word in ["schedule", "appointment", "book", "available"]):
        return "I can collect your preferred date and time. A team member can review and confirm the appointment."
    if any(word in text for word in ["photo", "picture"]):
        return "Photos can help the team understand the job. For this class prototype, add the important details in the quote form; live photo/SMS intake is a future integration."
    if any(word in text for word in ["hello", "hi", "hey"]):
        return "Hi! I’m the A to Z customer assistant. I can explain services, help start a quote, or collect a scheduling request."
    return "I can help with A to Z services, quote requests, and scheduling. For anything I’m not certain about, I’ll direct it to a team member."

init_db()

st.markdown('<div class="hero"><h1>💧 A to Z Power Washing</h1><div class="muted">AI Customer Communication System • Customer intake, leads, conversations, and scheduling in one place</div></div>', unsafe_allow_html=True)

page = st.sidebar.radio("Workspace", ["Customer Assistant", "Quote & Scheduling", "Owner Dashboard", "Conversations"])
st.sidebar.caption("Prototype implementation for A to Z Power Washing")

if page == "Customer Assistant":
    st.subheader("Customer Assistant")
    st.caption("Ask about services, quotes, or scheduling. The assistant avoids inventing prices or confirmed appointments.")
    if "chat" not in st.session_state:
        st.session_state.chat = [("assistant", "Welcome to A to Z Power Washing! How can I help you today?")]
    for role, msg in st.session_state.chat:
        with st.chat_message(role):
            st.write(msg)
    prompt = st.chat_input("Type a message...")
    if prompt:
        st.session_state.chat.append(("user", prompt))
        save_message("Customer", prompt)
        reply = assistant_reply(prompt)
        st.session_state.chat.append(("assistant", reply))
        save_message("A to Z Assistant", reply)
        st.rerun()

elif page == "Quote & Scheduling":
    st.subheader("Request a Quote or Appointment")
    st.write("Tell us about the job. The request is saved directly to the owner dashboard.")
    with st.form("lead_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        name = c1.text_input("Name *")
        phone = c2.text_input("Phone")
        email = c1.text_input("Email")
        service = c2.selectbox("Service *", SERVICES)
        address = st.text_input("Property address *")
        details = st.text_area("Job details", placeholder="Example: two-car concrete driveway with visible buildup")
        d1, d2 = st.columns(2)
        preferred_date = d1.date_input("Preferred date")
        preferred_time = d2.time_input("Preferred time")
        submitted = st.form_submit_button("Send Request", type="primary")
    if submitted:
        if not name.strip() or not address.strip():
            st.error("Please enter your name and property address.")
        else:
            lead_id = create_lead(name.strip(), phone.strip(), email.strip(), service, address.strip(),
                                  details.strip(), preferred_date, preferred_time)
            st.success(f"Request #{lead_id} received. A team member can now review it in the Owner Dashboard.")

elif page == "Owner Dashboard":
    st.subheader("Owner Dashboard")
    con = db()
    leads = pd.read_sql_query("SELECT * FROM leads ORDER BY id DESC", con)
    con.close()
    total = len(leads)
    new_count = int((leads["status"] == "New").sum()) if total else 0
    booked = int((leads["status"] == "Booked").sum()) if total else 0
    completed = int((leads["status"] == "Completed").sum()) if total else 0
    m1,m2,m3,m4 = st.columns(4)
    m1.metric("Total Leads", total); m2.metric("New", new_count); m3.metric("Booked", booked); m4.metric("Completed", completed)
    if leads.empty:
        st.info("No leads yet. Submit a test request from Quote & Scheduling.")
    else:
        st.dataframe(leads[["id","name","service","address","preferred_date","preferred_time","status","created_at"]],
                     use_container_width=True, hide_index=True)
        st.markdown("#### Update Lead")
        lead_id = st.selectbox("Lead", leads["id"].tolist(),
                               format_func=lambda x: f"#{x} — {leads.loc[leads.id==x,'name'].iloc[0]}")
        current = leads.loc[leads.id==lead_id, "status"].iloc[0]
        options = ["New","Contacted","Quoted","Booked","Completed","Closed"]
        status = st.selectbox("Status", options, index=options.index(current) if current in options else 0)
        if st.button("Save Status"):
            con = db(); con.execute("UPDATE leads SET status=? WHERE id=?", (status, int(lead_id))); con.commit(); con.close()
            st.success("Lead updated."); st.rerun()

else:
    st.subheader("Conversation Log")
    con = db()
    messages = pd.read_sql_query("SELECT * FROM messages ORDER BY id DESC", con)
    con.close()
    if messages.empty:
        st.info("No messages yet.")
    else:
        st.dataframe(messages[["id","lead_id","sender","message","created_at"]], use_container_width=True, hide_index=True)
        st.caption("This prototype logs assistant interactions locally. Real SMS/phone integration is intentionally not claimed.")
