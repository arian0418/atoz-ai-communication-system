import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
import shutil
from db import init_db, connect, create_lead, add_message, update_status, add_note, save_photo_record
from assistant import SERVICES, reply

UPLOADS=Path("uploads"); UPLOADS.mkdir(exist_ok=True)
init_db()
st.set_page_config(page_title="A to Z Power Washing | Communication Hub",page_icon="💧",layout="wide")
st.markdown("""<style>
.block-container{max-width:1200px;padding-top:1.5rem}.hero{padding:1.5rem 1.7rem;border:1px solid rgba(128,128,128,.25);border-radius:18px;margin-bottom:1rem}
.hero h1{margin:0;font-size:2.1rem}.muted{opacity:.7}[data-testid="stMetric"]{border:1px solid rgba(128,128,128,.2);padding:14px;border-radius:14px}
</style>""",unsafe_allow_html=True)
st.markdown('<div class="hero"><h1>💧 A to Z Power Washing</h1><div class="muted">Numa AI Implementation Prototype • Customer Communication • Quotes • Scheduling • CRM</div></div>',unsafe_allow_html=True)

page=st.sidebar.radio("Workspace",["Customer Assistant","Quote & Scheduling","Owner Dashboard","Lead Details","Appointments","Conversations","Reports"])
st.sidebar.caption("Numa AI Implementation Prototype • Python + SQL")

if page=="Customer Assistant":
    st.subheader("Numa AI Customer Assistant — Prototype")
    st.caption("Prototype of the Numa-based customer communication workflow proposed for A to Z Power Washing.")
    if "chat" not in st.session_state:
        st.session_state.chat=[("assistant","Welcome to A to Z Power Washing! How can I help?")]
    for role,msg in st.session_state.chat:
        with st.chat_message(role): st.write(msg)
    prompt=st.chat_input("Ask about services, quotes, photos, or scheduling...")
    if prompt:
        st.session_state.chat.append(("user",prompt)); add_message("Customer",prompt)
        _,ans=reply(prompt); st.session_state.chat.append(("assistant",ans)); add_message("A to Z Assistant",ans)
        st.rerun()

elif page=="Quote & Scheduling":
    st.subheader("Request a Quote or Appointment")
    st.write("Customer information is saved to the central lead dashboard.")
    with st.form("quote",clear_on_submit=True):
        a,b=st.columns(2)
        name=a.text_input("Name *"); phone=b.text_input("Phone")
        email=a.text_input("Email"); service=b.selectbox("Service *",SERVICES)
        address=st.text_input("Property address *")
        details=st.text_area("Job details",placeholder="Describe the surface, approximate size, buildup, access, or anything the crew should know.")
        c,d=st.columns(2); pdate=c.date_input("Preferred date"); ptime=d.time_input("Preferred time")
        photos=st.file_uploader("Job photos (optional)",type=["png","jpg","jpeg","webp"],accept_multiple_files=True)
        sent=st.form_submit_button("Submit Request",type="primary")
    if sent:
        if not name.strip() or not address.strip(): st.error("Name and property address are required.")
        else:
            lead_id=create_lead({"name":name.strip(),"phone":phone.strip(),"email":email.strip(),"service":service,
                "address":address.strip(),"details":details.strip(),"preferred_date":str(pdate),"preferred_time":str(ptime),"source":"Web Assistant"})
            add_message("Customer",f"Submitted a {service} request: {details or 'No extra details provided.'}",lead_id)
            add_message("A to Z Assistant","Request received and sent to the owner dashboard for human review.",lead_id)
            folder=UPLOADS/str(lead_id); folder.mkdir(parents=True,exist_ok=True)
            for f in photos:
                safe=Path(f.name).name; target=folder/safe
                with open(target,"wb") as out: shutil.copyfileobj(f,out)
                save_photo_record(lead_id,safe,str(target))
            st.success(f"Request #{lead_id} received. The appointment is requested, not confirmed.")

elif page=="Owner Dashboard":
    st.subheader("Owner Dashboard")
    con=connect(); leads=pd.read_sql_query("SELECT * FROM leads ORDER BY id DESC",con); con.close()
    total=len(leads); new=int((leads.status=="New").sum()) if total else 0; booked=int((leads.status=="Booked").sum()) if total else 0; done=int((leads.status=="Completed").sum()) if total else 0
    x1,x2,x3,x4=st.columns(4); x1.metric("Total Leads",total); x2.metric("New",new); x3.metric("Booked",booked); x4.metric("Completed",done)
    if leads.empty: st.info("No leads yet. Submit a test request from Quote & Scheduling.")
    else:
        status_filter=st.multiselect("Status filter",["New","Contacted","Quoted","Booked","Completed","Closed"],default=["New","Contacted","Quoted","Booked"])
        view=leads[leads.status.isin(status_filter)] if status_filter else leads
        st.dataframe(view[["id","name","phone","service","address","preferred_date","preferred_time","status","source","created_at"]],use_container_width=True,hide_index=True)
        csv=leads.to_csv(index=False).encode(); st.download_button("Export Leads CSV",csv,"atoz_leads.csv","text/csv")

elif page=="Lead Details":
    st.subheader("Lead Details & Follow-up")
    con=connect(); leads=pd.read_sql_query("SELECT * FROM leads ORDER BY id DESC",con); con.close()
    if leads.empty: st.info("No leads yet.")
    else:
        lead_id=st.selectbox("Choose lead",leads.id.tolist(),format_func=lambda x:f"#{x} — {leads.loc[leads.id==x,'name'].iloc[0]}")
        row=leads.loc[leads.id==lead_id].iloc[0]
        a,b=st.columns(2)
        with a:
            st.markdown(f"**Customer:** {row['name']}  \n**Phone:** {row['phone'] or '—'}  \n**Email:** {row['email'] or '—'}  \n**Address:** {row['address']}")
        with b:
            st.markdown(f"**Service:** {row['service']}  \n**Preferred:** {row['preferred_date']} {row['preferred_time']}  \n**Created:** {row['created_at']}")
        st.markdown("**Job details**"); st.write(row["details"] or "No details provided.")
        statuses=["New","Contacted","Quoted","Booked","Completed","Closed"]
        new_status=st.selectbox("Lead status",statuses,index=statuses.index(row["status"]) if row["status"] in statuses else 0)
        if st.button("Update Status",type="primary"): update_status(int(lead_id),new_status); st.success("Status updated."); st.rerun()
        note=st.text_area("Internal note")
        if st.button("Add Note") and note.strip(): add_note(int(lead_id),note.strip()); st.success("Note saved."); st.rerun()
        con=connect()
        notes=pd.read_sql_query("SELECT note,created_at FROM notes WHERE lead_id=? ORDER BY id DESC",con,params=(int(lead_id),))
        photos=pd.read_sql_query("SELECT original_name,stored_path FROM photos WHERE lead_id=?",con,params=(int(lead_id),))
        con.close()
        if not notes.empty: st.markdown("#### Internal Notes"); st.dataframe(notes,use_container_width=True,hide_index=True)
        if not photos.empty:
            st.markdown("#### Job Photos")
            for _,p in photos.iterrows():
                path=Path(p["stored_path"])
                if path.exists(): st.image(str(path),caption=p["original_name"],width=320)

elif page=="Appointments":
    st.subheader("Appointment Requests")
    con=connect()
    appts=pd.read_sql_query("""SELECT a.id,a.lead_id,l.name,l.service,l.address,a.appointment_date,a.appointment_time,a.status,a.notes
    FROM appointments a JOIN leads l ON l.id=a.lead_id ORDER BY a.appointment_date,a.appointment_time""",con)
    con.close()
    if appts.empty: st.info("No appointment requests.")
    else:
        st.dataframe(appts,use_container_width=True,hide_index=True)
        aid=st.selectbox("Appointment",appts.id.tolist())
        ast=st.selectbox("Appointment status",["Requested","Confirmed","Completed","Cancelled"])
        if st.button("Save Appointment Status"):
            con=connect(); con.execute("UPDATE appointments SET status=? WHERE id=?",(ast,int(aid))); con.commit(); con.close()
            st.success("Appointment updated."); st.rerun()

elif page=="Conversations":
    st.subheader("Central Conversation Log")
    con=connect(); msgs=pd.read_sql_query("SELECT * FROM messages ORDER BY id DESC",con); con.close()
    if msgs.empty: st.info("No conversations yet.")
    else:
        lead_filter=st.selectbox("Lead filter",["All"]+sorted([str(x) for x in msgs.lead_id.dropna().unique().tolist()]))
        view=msgs if lead_filter=="All" else msgs[msgs.lead_id==int(lead_filter)]
        st.dataframe(view[["id","lead_id","sender","channel","message","created_at"]],use_container_width=True,hide_index=True)

else:
    st.subheader("Reports")
    con=connect()
    leads=pd.read_sql_query("SELECT * FROM leads",con)
    msgs=pd.read_sql_query("SELECT * FROM messages",con)
    con.close()
    if leads.empty: st.info("Submit some test leads to populate reports.")
    else:
        a,b,c=st.columns(3); a.metric("Leads",len(leads)); b.metric("Conversations",len(msgs)); c.metric("Services Requested",leads.service.nunique())
        st.markdown("#### Leads by Status"); st.bar_chart(leads.status.value_counts())
        st.markdown("#### Requests by Service"); st.bar_chart(leads.service.value_counts())
        st.caption("These charts summarize data collected by this prototype. They do not claim real-world performance improvements.")
