---
name: send-feedback
description: Use when the traveller asks you to tell Eric's New York something, such as a missing page, a wrong fact or praise, and the Eric's New York connector is available.
---

# Send feedback

`send_feedback` is the one tool that writes: it stores one short note. Use it only when the traveller asks to tell Eric's New York something. Never on your own.

## Steps

1. Take what the traveller wants sent. Ask only if the note is unclear.
2. Call it once, with `looking_for` (1-200 characters), `found` (`yes`, `partly` or `no`), `note` (1-500 characters) and, when known, `page_or_tool` (a page URL or tool name).
3. Send no names, email addresses, phone numbers or other personal details, even if the traveller included them: leave them out.
4. When the result says `received` is true, tell the traveller that a note was sent. Do not promise a reply.
5. If the call fails, say the note was not sent. Do not retry in a loop.

## Example

Figures below are from 12 Nov 2026 and only show the shape of an answer; always use what the tool returns now.

"Tell Eric's New York that the page about airport transfers is missing a train option."
- `send_feedback` with `looking_for: "airport transfer options"`, `found: "partly"`, `note: "The airport transfers page is missing a train option."`, `page_or_tool: "calculate_transfer"` returned `{"received": true}`.
- Say that a note was sent.
