---
name: places-to-visit-eat-shop
description: Use when the user asks for places to visit, eat or shop in New York, things to do near a landmark, museums, or ideas by category, and the Eric's New York connector is available.
---

# Places to visit, eat or shop

Suggest only places the connector returned.

## Steps

1. Call `search_places` with at least one of `query` (part of a place name), `category` (for example "Museums") or `near` (the name of one of the guide's places; results are sorted by distance from it). `limit` is 1-20 (default 5).
2. For each place give its `name`, `address`, the guide's `tip` and, when it has one, the `ticket` link. Give `nearestSubway` when the traveller asks how to get there.
3. `ticket` carries a link and no price. Do not state a price for a place.
4. When `places` is empty, the `hint` says what to change: use a shorter name or another category, and try again once. Do not fill the gap from memory.

The tool does not find street addresses, and it has no `offset`.

## Example

Figures below are from 12 Nov 2026 and only show the shape of an answer; always use what the tool returns now.

"Suggest museums near the Top of the Rock."
- `search_places` with `near: "Top of the Rock"`, `category: "Museums"` and `limit: 3` returned MoMA (nearest stop 5 Av/53 St), Museum of Broadway and SPYSCAPE.
- Present each with its tip and link.
