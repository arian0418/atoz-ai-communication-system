# Final Prototype Status

This repository is the completed **Numa AI implementation prototype for A to Z Power Washing** described for the class demonstration.

## Completed workflow

Customer inquiry → automated response → quote/service intake → property details/photos → appointment request → centralized SQL record → owner review → lead status/follow-up → appointment confirmation → reporting.

## Demo-ready modules

1. Customer Assistant
2. Quote & Scheduling
3. Owner Dashboard
4. Lead Details & Follow-up
5. Appointments
6. Conversations
7. Reports

## What is real in this prototype

- Runnable Python/Streamlit application
- SQLite/SQL persistence
- Lead, message, appointment, photo, and note records
- Rule-based automated customer communication
- Human escalation behavior
- Quote and scheduling intake
- CRM-style lead workflow
- Reporting and CSV export
- Demo-data seeding and assistant unit tests

## Prototype boundary

The prototype demonstrates how the Numa AI workflow proposed in the report would operate for A to Z Power Washing. It does not connect to A to Z's real phone/SMS accounts or Numa's proprietary backend. Those require authorized production accounts and are outside the local prototype.

## Run

```powershell
python -m pip install -r requirements.txt
python seed_demo.py
python -m unittest test_assistant.py
python -m streamlit run app.py
```

For a clean demonstration, run `python seed_demo.py` once before opening the app.
