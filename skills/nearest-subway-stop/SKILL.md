---
name: nearest-subway-stop
description: Use when the user asks which subway stop is nearest to a New York attraction, hotel area or place, which lines stop there, how far it is to walk, or whether the stop is step-free, and the Eric's New York connector is available.
---

# Nearest subway stop

Answer from the connector. Do not name subway lines, stops or walking times from memory.

## Steps

1. If the user names a place, call `nearest_subway` with `place`. If the name is not found, call `search_places` with `query` and use the exact name it returns.
2. If the user gives coordinates in New York, call `nearest_subway` with `latitude` and `longitude`.
3. The tool does not find street addresses. For an address, ask for a place name or coordinates; do not guess coordinates.

## Reading the result

`stops` holds the three nearest stops, each with `name`, `lines`, `metres`, `walkMinutes` and `stepFree`. Give them as returned and say the walking time is an estimate from straight-line distance, not a routed walk. `search_places` cards already carry the two nearest stops (`nearestSubway`), so a second call is not needed when you have the card.

## Example

Figures below are from 12 Nov 2026 and only show the shape of an answer; always use what the tool returns now.

"Which subway stop is nearest to the Empire State Building, and is it step-free?"
- `nearest_subway` with `place: "Empire State Building"` returned 34 St - Herald Sq (lines B, F, D, M, R, Q, N, W), 184 metres, 3 minutes, `stepFree` true; then 28 St and 33 St, both not step-free.
- Present the three stops, with the estimate caveat.
