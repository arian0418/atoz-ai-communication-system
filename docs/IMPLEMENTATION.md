# Implementation Plan — Numa-Inspired A to Z System

## Project direction
The proposal originally selected Numa AI as the foundation for improving A to Z Power Washing's customer communication. During implementation, the team used the researched Numa communication model as inspiration and built its own version tailored to A to Z's workflow.

This is a change from directly deploying the third-party Numa product. The final implementation should be described as a **Numa-inspired system created by the team**, not as Numa software modified or owned by the team.

## Proposal requirements mapped to the implementation

| Proposal need | Team implementation |
| --- | --- |
| Faster customer responses | Customer Assistant |
| Service and FAQ responses | Rule-based approved knowledge |
| Quote intake | Quote & Scheduling form |
| Service type | Structured service selector |
| Address/property details | Lead intake fields |
| Customer photos | Multiple job-photo uploads |
| Scheduling | Preferred date/time + appointment request table |
| Central communication tracking | SQLite messages table + Conversations page |
| CRM-style lead organization | Owner Dashboard + lead pipeline |
| Human intervention | Explicit handoff behavior |
| Performance monitoring | Reports page |
| Staff follow-up | Lead Details + internal notes |

## Final demonstration
1. Customer asks the assistant for a driveway-cleaning quote.
2. Assistant explains that it needs property details rather than inventing a price.
3. Customer submits name, contact information, address, service, job details, a photo, and preferred appointment time.
4. A new lead appears in the Owner Dashboard.
5. Staff opens Lead Details, reviews the photo, adds a note, and updates the lead to Contacted/Quoted/Booked.
6. Staff confirms the appointment in Appointments.
7. Conversations shows centralized communication history.
8. Reports shows lead/status/service data stored in SQL.

## Production boundary
The software implements the workflow locally. Live SMS, phone routing, website-form ingestion, calendar synchronization, and external CRM integration require authorized business accounts and third-party services. They are extension points rather than fake integrations.
