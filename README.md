# A to Z Power Washing — AI Customer Communication System

A working class-project prototype that implements the customer communication workflow proposed for A to Z Power Washing.

## What it does

- Customer-facing communication assistant for common service, quote, and scheduling questions
- Structured quote and appointment intake
- SQLite database for leads and conversation history
- Owner dashboard with lead status tracking
- Central conversation log
- Human handoff behavior for questions the prototype should not answer
- Local, persistent data storage

The prototype is intentionally honest about its scope: it does **not** claim to be Numa's proprietary software, and it does not pretend to be connected to a live business phone number. It demonstrates the proposed workflow in a runnable system that can later be connected to real SMS/phone services.

## Technology

- Python
- Streamlit
- SQLite / SQL
- pandas

## Run on Windows

1. Install Python 3.10 or newer.
2. Open Command Prompt in this repository.
3. Install dependencies:

```
python -m pip install -r requirements.txt
```

4. Start the application:

```
python -m streamlit run app.py
```

5. Streamlit will open the application in your browser.

## Demo flow

1. Open **Customer Assistant** and ask: `How much does driveway cleaning cost?`
2. Open **Quote & Scheduling** and submit a sample customer request.
3. Open **Owner Dashboard** and show that the lead appeared automatically.
4. Change the lead from **New** to **Contacted**, **Quoted**, or **Booked**.
5. Open **Conversations** to demonstrate centralized communication records.

## Project scope

The system is based on the proposed A to Z workflow: customer intake, service questions, quote requests, scheduling requests, centralized lead tracking, and human follow-up. Real phone calls, SMS delivery, calendar synchronization, photo intake, and production CRM integration would require access to the business's accounts and third-party communication services.

## Data

The app creates `atoz_powerwashing.db` locally the first time it runs. The database is ignored by Git so test/customer data is not committed.
