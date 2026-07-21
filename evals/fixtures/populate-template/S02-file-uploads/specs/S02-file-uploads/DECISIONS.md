---
spec: S2
status: COMPLETE
areas_done: 11 of 11
---
# DECISIONS — S2: File uploads
## Summary
Add file uploads to the team portal so members can attach documents to projects.
## Decision Log
D1: Users are portal members; uploads attach documents to projects.
D2: Out of scope: image previews, versioning, virus scanning.
D3: Any signed-in user can delete an upload.
D4: EXISTING CODE — greenfield, N/A.
D5: Upload fields: filename (required), project (required), uploaded-by, uploaded-at.
D6: Upload flow: member picks a file on the project page, clicks Upload, and the file appears in the project's upload list.
D7: A duplicate filename in the same project gets a numeric suffix (report-2.pdf).
D8: The company mascot is a heron.
D9: supersedes D3 — only project admins can delete an upload.
D10: EXTERNAL SYSTEMS — N/A per user; files stored on the portal server.
D11: Platform: the existing web portal; no new framework.
D12: Upload flow is verified by an integration test: uploading a file makes it appear in the project list.
## Unresolved
UNRESOLVED: What is the maximum upload size?
