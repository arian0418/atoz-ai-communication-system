# A to Z Power Washing — Customer Communication System

A full-stack prototype built for a small power-washing business to organize customer inquiries, quote requests, appointments, messages, job photos, and follow-up.

## Why We Built This
A to Z Power Washing is a company owned by a friend of mine. Our group explored how software could make customer communication easier and keep potential jobs from getting lost between messages, quote requests, and scheduling.

The workflow was inspired by the customer-communication approach discussed in our Numa AI proposal, but this repository is our own implementation and does not reproduce Numa's proprietary software.

## Features
- React business dashboard with live SQLite data
- Customer/lead pipeline and status updates
- Customer detail view and internal notes
- Quote and appointment request form
- Multiple job-photo uploads
- Appointment status management
- Central message history
- Customer assistant with human-handoff rules
- Reports by pipeline status and requested service
- Python/Flask API
- SQLite persistence

## Technology
- React + Vite
- Python + Flask
- SQLite / SQL
- Lucide icons

## Run on Windows
Install Python and Node.js first. Then, from the project folder:

```
python -m pip install -r requirements.txt
npm install
npm run dev
```

`npm run dev` starts both the Python API and the Vite frontend. Open the Local URL shown by Vite, normally `http://localhost:5173`.

## Demo flow
1. Open Dashboard.
2. Add a customer through New Request.
3. Return to Dashboard and confirm the request appears.
4. Open Customers, change the lead status, and add an internal note.
5. Open Appointments and confirm the requested appointment.
6. Ask the Customer Assistant about pricing or scheduling.
7. Open Messages to see the conversation log.
8. Open Reports to see summaries from the SQLite data.

## Production boundary
This is a local prototype. It does not control A to Z's real phone number or provide live SMS, phone calls, calendar synchronization, payment processing, or production CRM connections. Those require authorized third-party accounts and production integrations.

Do not commit real customer information, local database files, uploaded photos, environment files, or secrets.
