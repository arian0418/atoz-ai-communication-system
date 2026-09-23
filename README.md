# A to Z Power Washing — Customer Communication System

A full-stack customer and lead management prototype for a small power-washing business. The project focuses on one practical problem: keeping customer requests, estimates, scheduling, messages, photos, and follow-up organized in one place.

## About the Project
This project was developed as part of a team effort to explore how software could improve customer communication for A to Z Power Washing. Our group focused on the challenges of keeping customer requests, quotes, appointments, messages, and follow-ups organized in one place. We designed and developed a system that brings these parts of the customer workflow together into a single application.

The workflow was inspired by the customer-communication problem discussed in our Numa AI proposal, but this repository is our own implementation. It does not reproduce Numa's proprietary software or claim to connect to Numa.

## What It Does
- Dashboard with live request, quote, booking, and completion counts
- Customer pipeline: New → Contacted → Quoted → Booked → Completed
- Searchable customer list and customer detail drawer
- Contact details, request information, internal notes, and activity history
- Quote creation with Draft, Sent, Accepted, and Declined states
- Accepting a quote moves the customer into the booked pipeline
- Appointment requests with Requested, Confirmed, Completed, and Cancelled states
- New-request form with multiple job-photo uploads
- Conversation inbox built from stored customer/assistant messages
- Customer assistant for supported service, quote, photo, and scheduling questions
- Human handoff language for complaints, damage, emergencies, and unsupported questions
- Reports for pipeline status, service demand, message count, quote count, and accepted quote value
- Persistent local SQLite storage

## Stack
**Frontend:** React, Vite, Lucide React  
**Backend:** Python, Flask  
**Database:** SQLite / SQL

The application follows a simple architecture:

```
React UI
   ↓ /api
Flask REST API
   ↓
Python business logic
   ↓
SQLite
```

## Run It on Windows
Requirements: Python 3 and Node.js/npm.

```cmd
python -m pip install -r requirements.txt
npm install
npm run dev
```

`npm run dev` starts the Flask API and Vite frontend together. Open the Local address shown by Vite, normally:

```
http://localhost:5173
```

To stop both processes, press `Ctrl+C`.

## Good Demo Flow
1. Create a customer from **New Request** and choose a preferred date.
2. Confirm the customer appears on **Dashboard** and **Customers**.
3. Open the customer, add an internal note, and create a quote.
4. Change the quote to **Accepted** and see the customer move to **Booked**.
5. Open **Appointments** and confirm or complete the requested appointment.
6. Ask the **Customer Assistant** about pricing or scheduling.
7. Open **Messages** to view the stored conversation.
8. Open **Reports** to see the updated business summary.

## Local Data and Safety
This repository intentionally ignores local databases, uploads, Node modules, environment files, Streamlit secrets, and build output. Do not commit real customer information or credentials.

The upload endpoint accepts JPG, JPEG, PNG, and WEBP filenames after sanitization. This is still a local educational prototype, not a hardened public production service.

## Scope
This project does **not** provide live SMS, phone calls, payment processing, calendar synchronization, production authentication, or a real CRM integration. Those features require authorized external services and are intentionally outside the scope of this portfolio version.

The customer assistant is a deterministic Python assistant, not a claim of a production AI model.

## Project Structure
```
src/
  main.jsx       React application
  styles.css     A to Z visual system

api.py           Flask REST API
db.py            SQLite schema and data operations
assistant.py     Customer-assistant intent/reply logic
seed_demo.py     Optional fictional demo records
test_assistant.py
vite.config.js   Vite + local API proxy
```

## Optional Demo Data
On a fresh database:

```cmd
python seed_demo.py
```

The script adds fictional records only if the database does not already contain leads.

## Tests
```cmd
python -m unittest test_assistant.py
```

These tests cover the assistant's core intent and handoff behavior. End-to-end UI behavior should also be checked manually using the demo flow above.
