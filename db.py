import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path("atoz_powerwashing.db")

SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS leads (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 name TEXT NOT NULL, phone TEXT, email TEXT,
 service TEXT NOT NULL, address TEXT NOT NULL, details TEXT,
 preferred_date TEXT, preferred_time TEXT,
 status TEXT NOT NULL DEFAULT 'New',
 source TEXT NOT NULL DEFAULT 'Web Assistant',
 created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS messages (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 lead_id INTEGER, sender TEXT NOT NULL, message TEXT NOT NULL,
 channel TEXT NOT NULL DEFAULT 'Web',
 created_at TEXT NOT NULL,
 FOREIGN KEY (lead_id) REFERENCES leads(id) ON DELETE SET NULL
);
CREATE TABLE IF NOT EXISTS appointments (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 lead_id INTEGER NOT NULL, appointment_date TEXT NOT NULL,
 appointment_time TEXT, status TEXT NOT NULL DEFAULT 'Requested',
 notes TEXT, created_at TEXT NOT NULL,
 FOREIGN KEY (lead_id) REFERENCES leads(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS photos (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 lead_id INTEGER NOT NULL, original_name TEXT NOT NULL,
 stored_path TEXT NOT NULL, created_at TEXT NOT NULL,
 FOREIGN KEY (lead_id) REFERENCES leads(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS notes (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 lead_id INTEGER NOT NULL, note TEXT NOT NULL, created_at TEXT NOT NULL,
 FOREIGN KEY (lead_id) REFERENCES leads(id) ON DELETE CASCADE
);
"""

def connect():
    con=sqlite3.connect(DB_PATH,check_same_thread=False)
    con.row_factory=sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con

def init_db():
    con=connect(); con.executescript(SCHEMA); con.commit(); con.close()

def now(): return datetime.now().isoformat(timespec="seconds")

def create_lead(data):
    con=connect()
    cur=con.execute("""INSERT INTO leads
    (name,phone,email,service,address,details,preferred_date,preferred_time,status,source,created_at,updated_at)
    VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
    (data["name"],data.get("phone",""),data.get("email",""),data["service"],data["address"],
     data.get("details",""),data.get("preferred_date",""),data.get("preferred_time",""),
     "New",data.get("source","Web Assistant"),now(),now()))
    lead_id=cur.lastrowid
    if data.get("preferred_date"):
        con.execute("""INSERT INTO appointments
        (lead_id,appointment_date,appointment_time,status,notes,created_at)
        VALUES(?,?,?,?,?,?)""",(lead_id,data["preferred_date"],data.get("preferred_time",""),
        "Requested","Customer preferred time; not yet confirmed.",now()))
    con.commit(); con.close(); return lead_id

def add_message(sender,message,lead_id=None,channel="Web"):
    con=connect(); con.execute("INSERT INTO messages(lead_id,sender,message,channel,created_at) VALUES(?,?,?,?,?)",
        (lead_id,sender,message,channel,now())); con.commit(); con.close()

def update_status(lead_id,status):
    con=connect(); con.execute("UPDATE leads SET status=?,updated_at=? WHERE id=?",(status,now(),lead_id)); con.commit(); con.close()

def add_note(lead_id,note):
    con=connect(); con.execute("INSERT INTO notes(lead_id,note,created_at) VALUES(?,?,?)",(lead_id,note,now())); con.commit(); con.close()

def save_photo_record(lead_id,name,path):
    con=connect(); con.execute("INSERT INTO photos(lead_id,original_name,stored_path,created_at) VALUES(?,?,?,?)",
        (lead_id,name,path,now())); con.commit(); con.close()
