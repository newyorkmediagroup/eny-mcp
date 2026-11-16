---
name: broadway-shows-and-seats
description: Use when the user asks which Broadway shows are on, what a show costs, which performances have seats on a date, or how to choose between shows, and the Eric's New York connector is available.
---

# Broadway shows and seats

Report shows, prices and seats only as the connector returned them.

## Steps

1. When the traveller names a date and `list_broadway_shows` lists a `date` input, call it with that date (YYYY-MM-DD): one call returns each bookable show's lowest price that day, cheapest first. Otherwise call it with `query` for a show name. It returns a page: when the result has `nextOffset`, send that value as `offset` for the next page. The last page has no `nextOffset`.
2. A row with a `showId` is bookable. A row with no `showId` (`bookable` false, no venue or price) is a partner or affiliate page: give its `url` and do not call `get_performance_availability` for it.
3. For seats, ask for the date if the traveller gave none. Call `get_performance_availability` only for the few shows the traveller is interested in, never for every show, with `show_id` (a string) and `date` (YYYY-MM-DD).
4. Each performance has `date_label`, `description` (the seating area), `price`, `currency` and `amount`; the result does not say how many tickets a booking takes or how many are left. If `performances` is empty, say there are no performances that day.

## Prices

`priceFrom` and `amount` are per person, in the site's own currency: read `currency`. See the never-invent-prices-or-availability skill.

## Example

Figures below are from 12 Nov 2026 and only show the shape of an answer; always use what the tool returns now.

"Which seats are there for The Lion King on 10 December?"
- `list_broadway_shows` with `limit: 3` returned The Lion King, `showId` "LIONKING3", Minskoff Theatre, `priceFrom` 129.15 GBP per person.
- `get_performance_availability` with `show_id: "LIONKING3"` and `date: "2026-12-10"` returned the 19:00 performance with "Premiums" at 270.14 GBP and "Rear Orchestra" at 158.21 GBP.
- Present the areas and prices with the show's `url`.
