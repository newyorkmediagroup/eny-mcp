---
name: airport-transfers
description: Use when the user asks how to get from a New York airport (JFK, Newark, LaGuardia) to their hotel or area, what a taxi, shuttle or train costs, or which transfer suits their group, and the Eric's New York connector is available.
---

# Airport transfers

Report transfer options and prices only as the connector returned them.

## Steps

1. Ask only for what is missing: the airport, the area and the group size.
2. Call `list_transfer_options`. Match the airport to a `departures` id and the area to a `destinations` id. Never guess an id.
3. Call `calculate_transfer` with `persons`, `departure` and `destination`.
4. For each entry in `modes` give `name`, `amount` with `currency` (US dollars) and the `bookingUrl`. The `notes` explain the option. Ignore the flat `price` string; use `amount`.
5. `amount` is for the whole group (`basis` is `per_group`), not per person. Say so.
6. Entries in `skipped`, or a mode marked `unavailable`, have no price right now. Say that; never call them free.

## Example

Figures below are from 12 Nov 2026 and only show the shape of an answer; always use what the tool returns now.

"How do we get from JFK to Manhattan, four of us?"
- `list_transfer_options` returned JFK Airport (id 1) and Manhattan (id 3).
- `calculate_transfer` with `persons: 4`, `departure: 1`, `destination: 3` returned Taxi at 98 USD for the group, JFK AirTrain and Metro at 47 USD, Shared Shuttle bus at 180 USD.
- Present the options with the amounts, the group basis, and each `bookingUrl`.
