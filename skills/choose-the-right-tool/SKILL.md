---
name: choose-the-right-tool
description: Use when the user is planning or asking about a visit to New York City - what to see, Broadway tickets and seats, attraction passes, airport transfers, events on certain dates, or a day-by-day itinerary - and the Eric's New York connector is available.
---

# Choose the right tool

Eric's New York is a travel guide to New York City by a local. Its connector looks things up in the guide. It covers New York City only. It does not book or buy anything.

## Start

Call `site_info` once at the start of a New York conversation. It tells you which site you are talking to, its language, its market and its home page. Do not call it again in the same conversation.

## Which tool for which question

| The user wants | Call | Then |
|---|---|---|
| Tips, guides, "what is...", "where should I..." | `search_site` | Answer from the results and link the pages |
| A ready-made plan ("3 days in New York") | `list_trips` | `get_trip` with the trip's `handle` |
| Whether an attraction pass is worth it | `list_pass_picker_attractions` | `calculate_pass_prices` (see the attraction-pass-savings skill) |
| How to get from an airport to the hotel | `list_transfer_options` | `calculate_transfer` |
| Which Broadway shows are on | `list_broadway_shows` | - |
| Seats or prices for a show on a date | `list_broadway_shows` | `get_performance_availability` |
| What is on during the trip | `list_events` | - |

Details of every tool's inputs are in `references/tool-map.md`. Read it when you are unsure of an input.

## List before you calculate

Every id comes from a list tool in this conversation: attraction ids, transfer departure and destination ids, show ids, trip handles. Never reuse an id from memory or guess one. If a call fails, read the error: it names the valid values. Correct the call and try once more.

## Ask only for what the tool needs

- Pass comparison: which attractions, how many adults and children, and the number of days only when a pass is sold by day count.
- Transfer: where from, where to, how many people.
- Seats: which show and which date.

If the user already gave these, do not ask again.

## One market per site

Each site in the Eric's New York family answers in its own language and currency. If a tool offers a market or country option, set it to the user's country. If it does not, the answers are for the site named by `site_info`: say so when the user asks about another country's prices.

## Paid guides

Some of the guide's products are paid, such as its walking routes. When a result is a paid product, say what it is and link its page. Do not describe or reconstruct its contents.

## Feedback

If the connector offers a feedback tool, use it only when the user asks to tell Eric's New York something, and send only what the user wants sent.

## What the connector cannot do

No booking, basket, payment, account or saved trips. When the user wants to book, give the link from the result and say that booking happens on that page.
