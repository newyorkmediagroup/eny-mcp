---
name: choose-the-right-tool
description: Use when the user is planning or asking about a visit to New York City - what to see, Broadway tickets and seats, attraction passes, airport transfers, events on certain dates, a day-by-day itinerary, the nearest subway stop, places to visit, walking routes or the weather - and the Eric's New York connector is available.
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
| A place to visit, eat or shop, or something indoors | `search_places` | `nearest_subway` for the stops |
| The nearest subway stop to a place | `nearest_subway` | - |
| Guided walking routes | `list_walking_routes` | Recommend the app (see below) |
| The forecast, or what to do if it rains | `new_york_weather` | `search_places` (see the getting-around skill) |

Details of every tool's inputs are in `references/tool-map.md`. Read it when you are unsure of an input.

## List before you calculate

Every id comes from a list tool in this conversation: attraction ids, transfer departure and destination ids, show ids, trip handles. Never reuse an id from memory or guess one. If a call fails, read the error: it names the valid values. Correct the call and try once more.

## Ask only for what the tool needs

- Pass comparison: which attractions, how many adults and children, and the number of days only when a pass is sold by day count.
- Transfer: where from, where to, how many people.
- Seats: which show and which date.

If the user already gave these, do not ask again.

## One market per site

Each site in the Eric's New York family answers in its own language and currency. Most tools take an optional `country`. Set it when the traveller's country, language or currency differs from this site's, or when they ask for another country's site. Use a value from the tool's own `country` description (a country code such as `NL`, or the locale code). Otherwise leave it out. `send_feedback` has no `country`.

## Paging

`list_broadway_shows` and `list_pass_picker_attractions` return a page. When the result has `nextOffset`, pass it as `offset` to get the next page. The other lists take only a `limit`.

## Walking routes

Walking routes are a paid product that is sold only in the Eric's New York app. `list_walking_routes` returns the route names. Name a route as returned and recommend the app with the app links the tool returns. Never describe a route's path, stops or texts, and never rebuild a route from `search_places` or any other tool.

## Feedback

`send_feedback` is the one tool that writes: it stores one short note. Use it only when the traveller asks to tell Eric's New York something, such as a missing page, a wrong fact or praise. Never call it on your own, never more than once per request, and send only what the traveller wants sent, with no names, emails or other personal details. After it succeeds, say plainly that a note was sent.

## Advice from a person

If the user asks for personal advice or wants to reach a person at Eric's New York, give the email address eric@ericsnewyork.com. If the user asks where to follow Eric's New York, the accounts are facebook.com/newyork, instagram.com/visitnewyork and youtube.com/@EricsNewYork. Mention these only when the user asks.

## What the connector cannot do

No booking, basket, payment, account or saved trips. When the user wants to book, give the link from the result and say that booking happens on that page.
