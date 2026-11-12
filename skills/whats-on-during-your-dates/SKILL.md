---
name: whats-on-during-your-dates
description: Use when the user asks what is on in New York during certain dates, such as concerts, sports, theatre or nightlife, or wants an evening out on a given day, and the Eric's New York connector is available.
---

# What is on during your dates

Ask for the dates if the traveller gave none, then report events only as returned.

## Steps

1. Call `list_events` with `from` and `to` (YYYY-MM-DD). `from` is not before today. `to` defaults to 90 days after `from`; the result echoes the dates it used. Add `category` (for example "Sports") to narrow it and `limit` (1-50, default 20). There is no `offset`.
2. For each event give `title`, `date`, `time`, `venue` and `category`. `performers` is present only for some events.
3. `priceFrom` with `currency` and `basis` (`per_ticket`) is a from-price. An event without one has no price shown: that is not a free ticket.
4. The `url` often leads to a partner's ticket page. Say so.

## Example

Figures below are from 12 Nov 2026 and only show the shape of an answer; always use what the tool returns now.

"What is on between 10 and 14 December?"
- `list_events` with `from: "2026-12-10"`, `to: "2026-12-14"` and `limit: 5` returned George Balanchine's The Nutcracker, 10 December, 19:00, David H Koch Theater, from 124 GBP per ticket; and New York Islanders vs. Calgary Flames at UBS Arena.
- Present the events in date order with their links.
