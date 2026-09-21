# Test Plan

| Test | Action | Expected result |
| --- | --- | --- |
| Service question | Ask "What services do you offer?" | Assistant lists supported services |
| Price safety | Ask "How much is my driveway?" | Assistant does not invent a price |
| Human handoff | Mention damage/complaint | Assistant requests human follow-up |
| Quote intake | Submit required fields | New lead is stored |
| Missing fields | Submit without name/address | Validation blocks submission |
| Photo intake | Upload image with quote | Photo appears in Lead Details |
| Scheduling | Submit preferred date/time | Appointment appears as Requested |
| Lead workflow | Change New to Quoted/Booked | Status persists in SQL |
| Internal notes | Add employee note | Note persists on lead |
| Conversation log | Use assistant | Messages appear in Conversations |
| Reporting | Add multiple leads | Charts update from stored data |
| Export | Download leads CSV | CSV contains stored leads |

Run automated assistant tests with:

```
python -m unittest test_assistant.py
```

The full UI workflow should also be tested manually because it includes forms, uploads, and Streamlit session state.
