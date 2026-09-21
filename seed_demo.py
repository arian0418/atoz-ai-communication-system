from db import init_db, connect, create_lead, add_message, add_note

init_db()
con=connect()
count=con.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
con.close()

if count:
    print("Database already contains leads. Demo data was not added.")
else:
    samples=[
      {"name":"Jordan Lee","phone":"555-0101","email":"jordan@example.com","service":"Driveway Cleaning","address":"123 Demo Street","details":"Two-car concrete driveway with buildup.","preferred_date":"2026-09-25","preferred_time":"10:00:00","source":"Demo"},
      {"name":"Taylor Morgan","phone":"555-0102","email":"taylor@example.com","service":"Gutter Care","address":"456 Sample Avenue","details":"Two-story home; requesting gutter service.","preferred_date":"2026-09-26","preferred_time":"13:30:00","source":"Demo"}
    ]
    for data in samples:
        lead_id=create_lead(data)
        add_message("Customer",f"Demo request for {data['service']}.",lead_id)
        add_message("A to Z Assistant","Request received and queued for human review.",lead_id)
        add_note(lead_id,"Demo lead created for presentation practice.")
    print("Added 2 demo leads.")
