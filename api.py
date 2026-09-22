from flask import Flask, jsonify, request
from pathlib import Path
from werkzeug.utils import secure_filename
from db import init_db, connect, create_lead, add_message, update_status, add_note, save_photo_record
from assistant import SERVICES, reply

app = Flask(__name__)
UPLOADS = Path("uploads")
UPLOADS.mkdir(exist_ok=True)
init_db()

def rows(sql, params=()):
    con=connect(); data=[dict(r) for r in con.execute(sql,params).fetchall()]; con.close(); return data

@app.get("/api/summary")
def summary():
    leads=rows("SELECT * FROM leads ORDER BY id DESC")
    appts=rows("""SELECT a.*,l.name,l.service,l.address FROM appointments a
                  JOIN leads l ON l.id=a.lead_id ORDER BY appointment_date,appointment_time""")
    return jsonify({"leads":leads,"appointments":appts,"services":SERVICES})

@app.get("/api/leads")
def leads():
    return jsonify(rows("SELECT * FROM leads ORDER BY id DESC"))

@app.get("/api/leads/<int:lead_id>")
def lead(lead_id):
    data=rows("SELECT * FROM leads WHERE id=?",(lead_id,))
    if not data: return jsonify({"error":"Customer not found"}),404
    return jsonify({"lead":data[0],
      "notes":rows("SELECT * FROM notes WHERE lead_id=? ORDER BY id DESC",(lead_id,)),
      "photos":rows("SELECT * FROM photos WHERE lead_id=? ORDER BY id DESC",(lead_id,))})

@app.post("/api/leads")
def new_lead():
    data=request.form
    if not data.get("name","").strip() or not data.get("address","").strip():
        return jsonify({"error":"Name and address are required."}),400
    lead_id=create_lead({k:data.get(k,"") for k in ["name","phone","email","service","address","details","preferred_date","preferred_time","source"]})
    add_message("Customer",f"Submitted a {data.get('service','service')} request: {data.get('details') or 'No extra details provided.'}",lead_id)
    folder=UPLOADS/str(lead_id); folder.mkdir(parents=True,exist_ok=True)
    for f in request.files.getlist("photos"):
        name=secure_filename(f.filename)
        if name:
            target=folder/name; f.save(target); save_photo_record(lead_id,name,str(target))
    return jsonify({"id":lead_id}),201

@app.patch("/api/leads/<int:lead_id>/status")
def lead_status(lead_id):
    status=request.json.get("status","")
    if status not in ["New","Contacted","Quoted","Booked","Completed","Closed"]:
        return jsonify({"error":"Invalid status"}),400
    update_status(lead_id,status); return jsonify({"ok":True})

@app.post("/api/leads/<int:lead_id>/notes")
def note(lead_id):
    text=request.json.get("note","").strip()
    if not text:return jsonify({"error":"Note is required"}),400
    add_note(lead_id,text); return jsonify({"ok":True}),201

@app.get("/api/messages")
def messages():
    return jsonify(rows("SELECT * FROM messages ORDER BY id DESC"))

@app.get("/api/appointments")
def appointments():
    return jsonify(rows("""SELECT a.*,l.name,l.service,l.address FROM appointments a
        JOIN leads l ON l.id=a.lead_id ORDER BY appointment_date,appointment_time"""))

@app.patch("/api/appointments/<int:appt_id>")
def appointment_status(appt_id):
    status=request.json.get("status","")
    if status not in ["Requested","Confirmed","Completed","Cancelled"]:
        return jsonify({"error":"Invalid status"}),400
    con=connect(); con.execute("UPDATE appointments SET status=? WHERE id=?",(status,appt_id)); con.commit(); con.close()
    return jsonify({"ok":True})

@app.post("/api/assistant")
def assistant():
    message=request.json.get("message","").strip()
    if not message:return jsonify({"error":"Message is required"}),400
    add_message("Customer",message)
    intent,answer=reply(message)
    add_message("A to Z Assistant",answer)
    return jsonify({"intent":intent,"answer":answer})

@app.get("/api/reports")
def reports():
    leads=rows("SELECT * FROM leads")
    messages=rows("SELECT * FROM messages")
    by_status={}; by_service={}
    for x in leads:
        by_status[x["status"]]=by_status.get(x["status"],0)+1
        by_service[x["service"]]=by_service.get(x["service"],0)+1
    return jsonify({"customers":len(leads),"messages":len(messages),"by_status":by_status,"by_service":by_service})

if __name__=="__main__":
    app.run(port=5000,debug=False)
