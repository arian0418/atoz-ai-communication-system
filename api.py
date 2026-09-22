from flask import Flask, jsonify, request, send_from_directory
from pathlib import Path
from werkzeug.utils import secure_filename
from db import init_db, connect, create_lead, add_message, update_status, add_note, save_photo_record, create_quote, log_activity, now
from assistant import SERVICES, reply

app=Flask(__name__)
UPLOADS=Path("uploads"); UPLOADS.mkdir(exist_ok=True)
ALLOWED_EXTENSIONS={".png",".jpg",".jpeg",".webp"}
init_db()

def rows(sql,params=()):
    con=connect(); data=[dict(r) for r in con.execute(sql,params).fetchall()]; con.close(); return data

def exists(lead_id): return bool(rows("SELECT id FROM leads WHERE id=?",(lead_id,)))

@app.get("/api/summary")
def summary():
    leads=rows("SELECT * FROM leads ORDER BY id DESC")
    appts=rows("""SELECT a.*,l.name,l.service,l.address FROM appointments a JOIN leads l ON l.id=a.lead_id
                  WHERE a.status!='Cancelled' ORDER BY appointment_date,appointment_time""")
    quotes=rows("SELECT * FROM quotes ORDER BY id DESC")
    return jsonify({"leads":leads,"appointments":appts,"quotes":quotes,"services":SERVICES})

@app.get("/api/leads")
def leads(): return jsonify(rows("SELECT * FROM leads ORDER BY id DESC"))

@app.get("/api/leads/<int:lead_id>")
def lead(lead_id):
    data=rows("SELECT * FROM leads WHERE id=?",(lead_id,))
    if not data:return jsonify({"error":"Customer not found"}),404
    return jsonify({"lead":data[0],
      "notes":rows("SELECT * FROM notes WHERE lead_id=? ORDER BY id DESC",(lead_id,)),
      "photos":rows("SELECT * FROM photos WHERE lead_id=? ORDER BY id DESC",(lead_id,)),
      "quotes":rows("SELECT * FROM quotes WHERE lead_id=? ORDER BY id DESC",(lead_id,)),
      "activity":rows("SELECT * FROM activity WHERE lead_id=? ORDER BY id DESC",(lead_id,)),
      "messages":rows("SELECT * FROM messages WHERE lead_id=? ORDER BY id DESC",(lead_id,))})

@app.post("/api/leads")
def new_lead():
    data=request.form
    required=["name","service","address"]
    if any(not data.get(k,"").strip() for k in required):return jsonify({"error":"Name, service, and address are required."}),400
    if data.get("service") not in SERVICES:return jsonify({"error":"Choose a valid service."}),400
    lead_id=create_lead({k:data.get(k,"").strip() for k in ["name","phone","email","service","address","details","preferred_date","preferred_time","source"]})
    add_message("Customer",f"Submitted a {data.get('service')} request: {data.get('details') or 'No extra details provided.'}",lead_id)
    folder=UPLOADS/str(lead_id); folder.mkdir(parents=True,exist_ok=True)
    for f in request.files.getlist("photos"):
        name=secure_filename(f.filename)
        ext=Path(name).suffix.lower()
        if name and ext in ALLOWED_EXTENSIONS:
            target=folder/name; f.save(target); save_photo_record(lead_id,name,str(target))
    return jsonify({"id":lead_id}),201

@app.patch("/api/leads/<int:lead_id>/status")
def lead_status(lead_id):
    if not exists(lead_id):return jsonify({"error":"Customer not found"}),404
    status=(request.json or {}).get("status","")
    if status not in ["New","Contacted","Quoted","Booked","Completed","Closed"]:return jsonify({"error":"Invalid status"}),400
    update_status(lead_id,status); return jsonify({"ok":True})

@app.post("/api/leads/<int:lead_id>/notes")
def note(lead_id):
    if not exists(lead_id):return jsonify({"error":"Customer not found"}),404
    text=(request.json or {}).get("note","").strip()
    if not text:return jsonify({"error":"Note is required"}),400
    add_note(lead_id,text); return jsonify({"ok":True}),201

@app.post("/api/leads/<int:lead_id>/quotes")
def quote(lead_id):
    if not exists(lead_id):return jsonify({"error":"Customer not found"}),404
    data=request.json or {}; description=data.get("description","").strip()
    try: amount=float(data.get("amount",0))
    except (TypeError,ValueError):return jsonify({"error":"Enter a valid quote amount."}),400
    if not description or amount<0:return jsonify({"error":"Description and a non-negative amount are required."}),400
    qid=create_quote(lead_id,description,amount); update_status(lead_id,"Quoted")
    return jsonify({"id":qid}),201

@app.patch("/api/quotes/<int:quote_id>")
def quote_status(quote_id):
    status=(request.json or {}).get("status","")
    if status not in ["Draft","Sent","Accepted","Declined"]:return jsonify({"error":"Invalid quote status"}),400
    q=rows("SELECT * FROM quotes WHERE id=?",(quote_id,))
    if not q:return jsonify({"error":"Quote not found"}),404
    con=connect(); con.execute("UPDATE quotes SET status=?,updated_at=? WHERE id=?",(status,now(),quote_id))
    log_activity(q[0]["lead_id"],f"Quote marked {status}",con); con.commit(); con.close()
    if status=="Accepted": update_status(q[0]["lead_id"],"Booked")
    return jsonify({"ok":True})

@app.get("/api/messages")
def messages():
    return jsonify(rows("""SELECT m.*,l.name FROM messages m LEFT JOIN leads l ON l.id=m.lead_id ORDER BY m.id DESC"""))

@app.get("/api/appointments")
def appointments():
    return jsonify(rows("""SELECT a.*,l.name,l.service,l.address,l.phone FROM appointments a
        JOIN leads l ON l.id=a.lead_id ORDER BY appointment_date,appointment_time"""))

@app.patch("/api/appointments/<int:appt_id>")
def appointment_status(appt_id):
    status=(request.json or {}).get("status","")
    if status not in ["Requested","Confirmed","Completed","Cancelled"]:return jsonify({"error":"Invalid status"}),400
    a=rows("SELECT * FROM appointments WHERE id=?",(appt_id,))
    if not a:return jsonify({"error":"Appointment not found"}),404
    con=connect(); con.execute("UPDATE appointments SET status=? WHERE id=?",(status,appt_id))
    log_activity(a[0]["lead_id"],f"Appointment marked {status}",con); con.commit(); con.close()
    if status=="Confirmed":update_status(a[0]["lead_id"],"Booked")
    if status=="Completed":update_status(a[0]["lead_id"],"Completed")
    return jsonify({"ok":True})

@app.post("/api/assistant")
def assistant():
    data=request.json or {}; message=data.get("message","").strip(); lead_id=data.get("lead_id")
    if not message:return jsonify({"error":"Message is required"}),400
    if lead_id and not exists(lead_id):lead_id=None
    add_message("Customer",message,lead_id)
    intent,answer=reply(message); add_message("A to Z Assistant",answer,lead_id)
    return jsonify({"intent":intent,"answer":answer})

@app.get("/api/reports")
def reports():
    leads=rows("SELECT * FROM leads"); messages=rows("SELECT * FROM messages"); quotes=rows("SELECT * FROM quotes")
    by_status={}; by_service={}
    for x in leads:
        by_status[x["status"]]=by_status.get(x["status"],0)+1
        by_service[x["service"]]=by_service.get(x["service"],0)+1
    accepted=sum(float(q["amount"]) for q in quotes if q["status"]=="Accepted")
    return jsonify({"customers":len(leads),"messages":len(messages),"quotes":len(quotes),"accepted_value":accepted,
                    "by_status":by_status,"by_service":by_service})

@app.get("/uploads/<int:lead_id>/<path:name>")
def upload(lead_id,name): return send_from_directory(UPLOADS/str(lead_id),name)

if __name__=="__main__": app.run(host="127.0.0.1",port=5000,debug=False)
