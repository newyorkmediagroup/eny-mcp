---
name: getting-around
description: Use when the user asks which subway stop is nearest to a New York place, how to reach it, what the weather will be on a date, or what to do if it rains, and the Eric's New York connector is available.
---

# Getting around

Answer from the connector. Do not name subway lines, stops, walking times or weather from memory.

## Nearest subway stop

1. If the user names a place, call `nearest_subway` with `place` set to the name. If the name is not found, call `search_places` with `query` and use the exact name it returns.
2. If the user gives coordinates in New York, call `nearest_subway` with `latitude` and `longitude`.
3. `nearest_subway` cannot find a street address. If the user gives only an address, ask for a place name or coordinates. Do not guess coordinates.

The tool returns the three nearest stops with their lines, the distance in metres, an estimated walking time and whether the stop is step-free. Give those as returned and say the walking time is an estimate from straight-line distance, not a routed walk.

`search_places` cards also carry the two nearest stops of that place, so a second call is not needed when you already have the card.

## Weather and a rain plan

1. Call `new_york_weather` with `date` (YYYY-MM-DD) for one day, or without it for the whole forecast. The forecast runs about 7 days ahead. If the date is outside it, the tool says so: report that, and do not predict.
2. Report temperature in the unit the traveller uses (the result gives Fahrenheit and Celsius), the short description and the chance of rain. The description is in English, as the National Weather Service wrote it.
3. When the result has a `rain_plan`, call `search_places` with a category it names (for example `category: "Museums"` or `"Theatres"`) and offer places from that result. Link the guide article from the plan when it has one. Suggest only places the tool returned.
4. When the result has no `rain_plan`, do not suggest a rain plan.

Say when the forecast was fetched if the conversation runs on, because forecasts change.

## Walking routes

If the traveller wants a guided walk, call `list_walking_routes`. Routes are a paid product sold only in the Eric's New York app. Name the route as the tool returns it and recommend the app using the app links in the result. Never describe a route's path, stops or texts, and never rebuild one from `search_places` or `nearest_subway`.
