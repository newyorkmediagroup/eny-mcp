---
name: weather-and-rain-plan
description: Use when the user asks what the weather will be in New York on a date or during their trip, whether to pack for rain, or what to do indoors if it rains, and the Eric's New York connector is available.
---

# Weather and rain plan

Report the forecast from the connector. Do not state weather from memory.

## Steps

1. Call `new_york_weather` with `date` (YYYY-MM-DD) for one day, or without it for the whole forecast. It runs about 7 days ahead. For a date outside it the tool says so: report that and do not predict.
2. Each period has `name`, `temp_f`, `temp_c`, `forecast` and `rain_chance`. Give the temperature in the unit the traveller uses and the chance of rain as a percentage. `forecast` is in English, as the National Weather Service wrote it.
3. When the result has a `rain_plan`, call `search_places` with `category` set to one of its `indoor_categories` (for example "Museums") and offer places from that result. Link the plan's `article` when it has one.
4. When the result has no `rain_plan`, do not suggest one.

Say when the forecast was fetched (`fetched_at`) if the conversation runs on.

## Example

"Will it rain on 13 November?"
- `new_york_weather` with `date: "2026-11-13"` returned Friday, 46 F / 8 C, "Light Rain", `rain_chance` 100, and a `rain_plan` with `indoor_categories` "Museums" and "Theatres".
- `search_places` with `category: "Museums"` and `limit: 3` returned 9/11 Museum, American Museum of Natural History and others.
- Present the forecast, then those places with their links, then the rain article link.
