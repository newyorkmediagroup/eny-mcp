---
name: plan-a-first-trip
description: Use when a first- or second-time visitor asks for a day-by-day plan for New York, what to do on each day of a trip of a given length, or how to start planning a visit, and the Eric's New York connector is available.
---

# Plan a first trip

Build the plan from the guide's own itineraries, then add what is on and where to go. These are editorial plans, not the traveller's saved trips.

## Steps

1. Ask for the number of days and the travel dates if they are missing.
2. Call `list_trips` and pick the itinerary closest to the number of days. Call `get_trip` with its `handle`.
3. The plan is in `config`: `resources` are the days (`name` "Day 1") and `events` are the steps, each with `text` and the `resource` id of its day. The dates inside `events` are placeholders; use only the time of day, and no real date.
4. Call `list_events` with the travel dates for what is on. Call `search_places` (`category` or `near`) for extra places around a stop.
5. Present it day by day. Mark what comes from the itinerary, what is on, and what is a suggested place, each with its link. Do not add attractions, times or prices from memory.

## Example

"First visit, four days from 10 December. Where do we start?"
- `list_trips` returned the handle `nyc4days`. `get_trip` with `handle: "nyc4days"` returned "Day 1": Day of arrival, Arrival at hotel, Go to Times Square, Dinner at John's Pizza.
- `list_events` with `from: "2026-12-10"` and `to: "2026-12-14"` returned events by date; `search_places` with `category: "Museums"` returned places for a rainy day.
- Present Day 1 from the itinerary, then what is on that evening.
