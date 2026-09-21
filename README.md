# A to Z Power Washing — AI Customer Communication System

A complete, runnable prototype of the customer communication workflow designed for A to Z Power Washing.

## Why We Built This

A to Z Power Washing is a company owned by a friend of mine. As a group, we wanted to explore how technology could help the business improve customer communication and turn more inquiries into potential jobs.

We focused on the process of responding to customers, collecting information for quotes, handling scheduling requests, and keeping track of leads and conversations. We built this prototype to bring those tasks together in one system and demonstrate how AI-assisted customer communication could help the company respond to potential customers more efficiently.

Our approach was inspired by the customer-communication model used by Numa AI and adapted to the needs of a power-washing business. The prototype combines customer assistance, quote intake, scheduling requests, lead management, conversation tracking, and an employee dashboard.

## Implemented features

### Customer side
- Automated customer assistant for supported service, quote, photo, service-area, and scheduling questions
- Safe human handoff for complaints, damage, emergencies, and uncertain requests
- Quote intake with customer/contact information
- Service selection
- Property address and job details
- Preferred appointment date/time
- Multiple job-photo uploads
- Clear distinction between a requested appointment and a confirmed appointment

### Business side
- Central owner dashboard
- Lead pipeline: New → Contacted → Quoted → Booked → Completed / Closed
- Detailed lead view
- Internal follow-up notes
- Job-photo review
- Appointment request management
- Central conversation history
- CSV lead export
- Reporting for lead status and service demand

### Database
SQLite stores:
- leads
- messages
- appointments
- photos
- internal notes

This gives the project real SQL-backed persistence without requiring a separate database server.

## Technology
- Python
- Streamlit
- SQLite / SQL
- pandas

## Run on Windows

```
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

The application creates `atoz_powerwashing.db` automatically.

## Recommended class demo

1. Open **Customer Assistant** and ask about a driveway-cleaning quote.
2. Show that the assistant does not invent a price.
3. Open **Quote & Scheduling**, enter a sample customer, attach a sample property photo, and submit.
4. Open **Owner Dashboard** and show the new lead.
5. Open **Lead Details**, add an internal note, and move the lead through the pipeline.
6. Open **Appointments** and confirm the request.
7. Open **Conversations** to show centralized records.
8. Open **Reports** to show SQL-backed business data.

## Important production boundary

This repository implements the application and workflow. It does not claim to reproduce Numa's proprietary software or to already control A to Z's real phone number. Live phone calls, SMS delivery, calendar synchronization, and production CRM connections require authorized access to the business accounts and third-party services.

The prototype is deliberately designed so those integrations can be added later without pretending they already exist.

## Privacy

Local database files, uploaded customer photos, environment files, and Streamlit secrets are ignored by Git. Do not commit real customer information to the repository.


## Numa inspiration

The team's original proposal selected Numa AI as the basis for improving customer communication. For the implementation stage, the team took inspiration from that communication model and created its own version specifically for A to Z Power Washing.

This repository is the team's implementation. It is **not Numa's proprietary software** and does not claim to modify Numa's code.

## Project documentation

- `docs/KNOWLEDGE_BASE.md` — approved assistant behavior and business knowledge
- `docs/IMPLEMENTATION.md` — proposal-to-product feature mapping and demo flow
- `docs/PRESENTATION.md` — presentation explanation and talking points
- `docs/TEST_PLAN.md` — manual and automated testing checklist
