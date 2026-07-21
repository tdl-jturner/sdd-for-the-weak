---
spec: S1
status: COMPLETE
areas_done: 11 of 11
---
# DECISIONS — S1: Invoice manager
## Summary
A small internal tool for the finance team to create and track invoices.
## Decision Log
D1: Users are the finance team only (~10 people).
D2: Out of scope: payments, reminders, multi-currency.
D3: Only admins can delete invoices.
D4: Invoice deletion is a soft delete.
D5: EXISTING CODE — greenfield, N/A.
D6: Invoice fields: number (unique, required), client name (required), amount (required), status (draft/sent/paid).
D7: Create flow: user fills the form; clicking Save shows the invoice in the list with status draft.
D8: Duplicate invoice number on save shows the error "Invoice number already exists" and keeps the form contents.
D9: All finance team members can view and create invoices; only admins delete (see D3).
D10: EXTERNAL SYSTEMS — N/A per user; data stored locally.
D11: Platform: web app; must work in Chrome.
D12: Create flow is verified by an integration test: saving a valid invoice makes it appear in the list.
D13: Soft-deleted invoices are retained forever.
## Unresolved
