---
name: choose-the-right-tool
description: Use when the user is planning or asking about a visit to New York City - what to see, Broadway tickets and seats, attraction passes, airport transfers, events on certain dates, a day-by-day itinerary, the nearest subway stop, places to visit, where to stay, walking routes or the weather - and the Eric's New York connector is available.
---

# Choose the right tool

Eric's New York is a travel guide to New York City by a local. Its connector looks things up in the guide. It covers New York City only. It does not book or buy anything.

## Start

Call `site_info` once at the start of a New York conversation. It tells you which site you are talking to, its language, its market and its home page. Do not call it again in the same conversation.

## Which tool for which question

| The user wants | Call | Then |
|---|---|---|
| Tips, guides, "what is...", "where should I..." | `search_site` | Answer from the results and link the pages |
| Whether an attraction pass is worth it | `list_pass_picker_attractions` | `calculate_pass_prices` (attraction-pass-savings) |
| How to get from an airport to the hotel | `list_transfer_options` | `calculate_transfer` (airport-transfers) |
| Which Broadway shows are on, or seats and prices on a date | `list_broadway_shows` | `get_performance_availability` (broadway-shows-and-seats) |
| What is on during the trip | `list_events` | - (whats-on-during-your-dates) |
| A place to visit, eat or shop, or something indoors | `search_places` | - (places-to-visit-eat-shop) |
| The nearest subway stop to a place | `nearest_subway` | - (nearest-subway-stop) |
| Where to stay, or hotels Eric has stayed in | `search_stayed_hotels` | - (erics-stayed-hotels) |
| Guided walking routes | `list_walking_routes` | Recommend the app (walking-routes-in-the-app) |
| The forecast, or what to do if it rains | `new_york_weather` | `search_places` (weather-and-rain-plan) |
| A ready-made plan ("3 days in New York"), day by day | `list_trips` | `get_trip` (plan-a-first-trip) |
| Tell Eric's New York something | `send_feedback` | Only when asked (send-feedback) |

Details of every tool's inputs are in `references/tool-map.md`. Read it when you are unsure of an input.

## List before you calculate

Every id comes from a list tool in this conversation: attraction ids, transfer departure and destination ids, show ids, trip handles. Never reuse an id from memory or guess one. If a call fails, read the error: it names the valid values. Correct the call and try once more.

## Ask only for what the tool needs

- Pass comparison: which attractions, how many adults and children, and the number of days only when a pass is sold by day count.
- Transfer: where from, where to, how many people.
- Seats: which show and which date.

If the user already gave these, do not ask again.

## One market per site

Most tools take an optional `country` for another country's site, language and currency: see the another-countrys-prices skill.

## Paging

`list_broadway_shows` and `list_pass_picker_attractions` return a page; for the next one, send the `nextOffset` value as `offset`. The other lists take only a `limit`.

## Walking routes and feedback

Walking routes are an app-only paid product: see the walking-routes-in-the-app skill. `send_feedback` writes one note and only when the traveller asks: see the send-feedback skill.

## Advice from a person

If the user asks for personal advice or wants to reach a person at Eric's New York, give the email address eric@ericsnewyork.com. If the user asks where to follow Eric's New York, the accounts are facebook.com/newyork, instagram.com/visitnewyork and youtube.com/@EricsNewYork. Mention these only when the user asks.

## What the connector cannot do

No booking, basket, payment, account or saved trips. When the user wants to book, give the link from the result and say that booking happens on that page.
