import streamlit as st
import pandas as pd
from pathlib import Path
import shutil
from db import init_db, connect, create_lead, add_message, update_status, add_note, save_photo_record
from assistant import SERVICES, reply

UPLOADS = Path("uploads")
UPLOADS.mkdir(exist_ok=True)
init_db()

st.set_page_config(page_title="A to Z Power Washing", page_icon="💧", layout="wide")

st.markdown("""
<style>
.stApp { background: #f8fafc; }
.block-container { max-width: 1180px; padding-top: 1.8rem; padding-bottom: 3rem; }
[data-testid="stSidebar"] { background: #ffffff; border-right: 1px solid #e5e7eb; }
[data-testid="stSidebar"] .block-container { padding-top: 1.5rem; }
h1,h2,h3 { letter-spacing: -0.025em; color: #111827; }
p, label { color: #374151; }
.brand { padding: .25rem 0 1.25rem; border-bottom: 1px solid #e5e7eb; margin-bottom: 1rem; }
.brand-title { font-size: 1.1rem; font-weight: 700; color: #111827; }
.brand-subtitle { font-size: .82rem; color: #6b7280; margin-top: .15rem; }
.page-heading { margin-bottom: 1.5rem; }
.page-heading h1 { font-size: 1.8rem; margin: 0 0 .25rem; }
.page-heading p { color: #6b7280; margin: 0; }
[data-testid="stMetric"] { background: #fff; border: 1px solid #e5e7eb; border-radius: 10px; padding: 1rem; box-shadow: 0 1px 2px rgba(0,0,0,.03); }
[data-testid="stMetricLabel"] { color: #6b7280; }
[data-testid="stDataFrame"] { border: 1px solid #e5e7eb; border-radius: 10px; overflow: hidden; }
.stButton > button, .stDownloadButton > button { border-radius: 8px; font-weight: 600; }
div[data-baseweb="input"] > div, div[data-baseweb="select"] > div, textarea { border-radius: 8px !important; }
.section { font-size: .9rem; font-weight: 700; color: #374151; margin: 1.5rem 0 .6rem; }
.helper { color: #6b7280; font-size: .9rem; }
hr { border-color: #e5e7eb; }
</style>
""", unsafe_allow_html=True)

st.sidebar.markdown(
    '<div class="brand"><div class="brand-title">A to Z Power Washing</div>'
    '<div class="brand-subtitle">Customer Communication System</div></div>',
    unsafe_allow_html=True,
)

PAGES = [
    "Dashboard", "Customers", "Messages", "Appointments",
    "New Request", "Customer Assistant", "Reports"
]
page = st.sidebar.radio("Navigation", PAGES, label_visibility="collapsed")
st.sidebar.divider()
st.sidebar.caption("Local prototype • Python + SQLite")

def heading(title, subtitle):
    st.markdown(
        f'<div class="page-heading"><h1>{title}</h1><p>{subtitle}</p></div>',
        unsafe_allow_html=True,
    )

def load_leads():
    con = connect()
    df = pd.read_sql_query("SELECT * FROM leads ORDER BY id DESC", con)
    con.close()
    return df

if page == "Dashboard":
    heading("Dashboard", "A quick view of customer requests and current work.")
    leads = load_leads()
    total = len(leads)
    new = int((leads.status == "New").sum()) if total else 0
    booked = int((leads.status == "Booked").sum()) if total else 0
    completed = int((leads.status == "Completed").sum()) if total else 0
    a,b,c,d = st.columns(4)
    a.metric("Total customers", total)
    b.metric("New requests", new)
    c.metric("Booked", booked)
    d.metric("Completed", completed)

    st.markdown('<div class="section">Recent requests</div>', unsafe_allow_html=True)
    if leads.empty:
        st.info("No customer requests yet. Use New Request to add a test customer.")
    else:
        st.dataframe(
            leads[["id","name","service","preferred_date","status","created_at"]].head(10),
            use_container_width=True, hide_index=True,
            column_config={"id":"ID","name":"Customer","service":"Service",
                           "preferred_date":"Preferred date","status":"Status","created_at":"Created"}
        )

elif page == "Customers":
    heading("Customers", "Review leads, update their status, and keep follow-up notes.")
    leads = load_leads()
    if leads.empty:
        st.info("No customers yet.")
    else:
        statuses = ["New","Contacted","Quoted","Booked","Completed","Closed"]
        selected = st.multiselect("Filter by status", statuses, default=["New","Contacted","Quoted","Booked"])
        view = leads[leads.status.isin(selected)] if selected else leads
        st.dataframe(
            view[["id","name","phone","service","address","status","created_at"]],
            use_container_width=True, hide_index=True
        )
        st.download_button("Export customer list", leads.to_csv(index=False).encode(),
                           "atoz_customers.csv", "text/csv")

        st.divider()
        st.subheader("Customer details")
        lead_id = st.selectbox(
            "Customer",
            leads.id.tolist(),
            format_func=lambda x: f"#{x} — {leads.loc[leads.id==x,'name'].iloc[0]}"
        )
        row = leads.loc[leads.id == lead_id].iloc[0]
        left, right = st.columns(2)
        with left:
            st.markdown(f"**Phone**  \n{row['phone'] or '—'}")
            st.markdown(f"**Email**  \n{row['email'] or '—'}")
            st.markdown(f"**Address**  \n{row['address']}")
        with right:
            st.markdown(f"**Service**  \n{row['service']}")
            st.markdown(f"**Preferred time**  \n{row['preferred_date']} {row['preferred_time']}")
            st.markdown(f"**Source**  \n{row['source']}")
        st.markdown("**Job details**")
        st.write(row["details"] or "No details provided.")

        new_status = st.selectbox(
            "Status", statuses,
            index=statuses.index(row["status"]) if row["status"] in statuses else 0
        )
        if st.button("Save status", type="primary"):
            update_status(int(lead_id), new_status)
            st.success("Customer status updated.")
            st.rerun()

        note = st.text_area("Internal note", placeholder="Add a note for the team...")
        if st.button("Add note") and note.strip():
            add_note(int(lead_id), note.strip())
            st.success("Note saved.")
            st.rerun()

        con = connect()
        notes = pd.read_sql_query(
            "SELECT note,created_at FROM notes WHERE lead_id=? ORDER BY id DESC",
            con, params=(int(lead_id),)
        )
        photos = pd.read_sql_query(
            "SELECT original_name,stored_path FROM photos WHERE lead_id=?",
            con, params=(int(lead_id),)
        )
        con.close()
        if not notes.empty:
            st.markdown('<div class="section">Notes</div>', unsafe_allow_html=True)
            st.dataframe(notes, use_container_width=True, hide_index=True)
        if not photos.empty:
            st.markdown('<div class="section">Job photos</div>', unsafe_allow_html=True)
            for _, p in photos.iterrows():
                path = Path(p["stored_path"])
                if path.exists():
                    st.image(str(path), caption=p["original_name"], width=300)

elif page == "Messages":
    heading("Messages", "Customer and assistant messages stored in one place.")
    con = connect()
    msgs = pd.read_sql_query("SELECT * FROM messages ORDER BY id DESC", con)
    con.close()
    if msgs.empty:
        st.info("No messages yet.")
    else:
        choices = ["All"] + sorted([str(x) for x in msgs.lead_id.dropna().unique().tolist()])
        lead_filter = st.selectbox("Customer ID", choices)
        view = msgs if lead_filter == "All" else msgs[msgs.lead_id == int(lead_filter)]
        st.dataframe(
            view[["lead_id","sender","channel","message","created_at"]],
            use_container_width=True, hide_index=True
        )

elif page == "Appointments":
    heading("Appointments", "Review requested times and confirm completed work.")
    con = connect()
    appts = pd.read_sql_query("""SELECT a.id,a.lead_id,l.name,l.service,l.address,
        a.appointment_date,a.appointment_time,a.status,a.notes
        FROM appointments a JOIN leads l ON l.id=a.lead_id
        ORDER BY a.appointment_date,a.appointment_time""", con)
    con.close()
    if appts.empty:
        st.info("No appointment requests yet.")
    else:
        st.dataframe(appts, use_container_width=True, hide_index=True)
        st.divider()
        aid = st.selectbox(
            "Appointment",
            appts.id.tolist(),
            format_func=lambda x: f"#{x} — {appts.loc[appts.id==x,'name'].iloc[0]}"
        )
        current = appts.loc[appts.id == aid, "status"].iloc[0]
        appt_statuses = ["Requested","Confirmed","Completed","Cancelled"]
        ast = st.selectbox(
            "Status", appt_statuses,
            index=appt_statuses.index(current) if current in appt_statuses else 0
        )
        if st.button("Save appointment", type="primary"):
            con = connect()
            con.execute("UPDATE appointments SET status=? WHERE id=?", (ast, int(aid)))
            con.commit(); con.close()
            st.success("Appointment updated.")
            st.rerun()

elif page == "New Request":
    heading("New Request", "Collect the information needed for a quote or appointment.")
    with st.form("request", clear_on_submit=True):
        a,b = st.columns(2)
        name = a.text_input("Customer name *")
        phone = b.text_input("Phone")
        email = a.text_input("Email")
        service = b.selectbox("Service *", SERVICES)
        address = st.text_input("Property address *")
        details = st.text_area(
            "Job details",
            placeholder="Surface, approximate size, buildup, access, or anything the crew should know."
        )
        c,d = st.columns(2)
        pdate = c.date_input("Preferred date")
        ptime = d.time_input("Preferred time")
        photos = st.file_uploader(
            "Job photos", type=["png","jpg","jpeg","webp"], accept_multiple_files=True
        )
        sent = st.form_submit_button("Save request", type="primary")

    if sent:
        if not name.strip() or not address.strip():
            st.error("Customer name and property address are required.")
        else:
            lead_id = create_lead({
                "name":name.strip(),"phone":phone.strip(),"email":email.strip(),
                "service":service,"address":address.strip(),"details":details.strip(),
                "preferred_date":str(pdate),"preferred_time":str(ptime),"source":"Web Assistant"
            })
            add_message("Customer", f"Submitted a {service} request: {details or 'No extra details provided.'}", lead_id)
            add_message("A to Z Assistant", "Request received and sent to the team for review.", lead_id)
            folder = UPLOADS / str(lead_id)
            folder.mkdir(parents=True, exist_ok=True)
            for f in photos:
                safe = Path(f.name).name
                target = folder / safe
                with open(target, "wb") as out:
                    shutil.copyfileobj(f, out)
                save_photo_record(lead_id, safe, str(target))
            st.success(f"Request #{lead_id} saved. The appointment is requested, not confirmed.")

elif page == "Customer Assistant":
    heading("Customer Assistant", "Answers common questions and sends uncertain issues to a person.")
    st.caption("Demo assistant for the A to Z customer communication workflow.")
    if "chat" not in st.session_state:
        st.session_state.chat = [
            ("assistant", "Hi! How can I help with your A to Z Power Washing request?")
        ]
    for role, msg in st.session_state.chat:
        with st.chat_message(role):
            st.write(msg)
    prompt = st.chat_input("Ask about services, quotes, photos, or scheduling...")
    if prompt:
        st.session_state.chat.append(("user", prompt))
        add_message("Customer", prompt)
        _, ans = reply(prompt)
        st.session_state.chat.append(("assistant", ans))
        add_message("A to Z Assistant", ans)
        st.rerun()

else:
    heading("Reports", "Simple summaries from the customer records in this prototype.")
    con = connect()
    leads = pd.read_sql_query("SELECT * FROM leads", con)
    msgs = pd.read_sql_query("SELECT * FROM messages", con)
    con.close()
    if leads.empty:
        st.info("Add some test customers to populate reports.")
    else:
        a,b,c = st.columns(3)
        a.metric("Customers", len(leads))
        b.metric("Messages", len(msgs))
        c.metric("Services requested", leads.service.nunique())
        left,right = st.columns(2)
        with left:
            st.markdown('<div class="section">Customers by status</div>', unsafe_allow_html=True)
            st.bar_chart(leads.status.value_counts())
        with right:
            st.markdown('<div class="section">Requests by service</div>', unsafe_allow_html=True)
            st.bar_chart(leads.service.value_counts())
        st.caption("Reports use local prototype data and do not represent real business performance.")
