# Tool map

One entry per tool: what it needs, where its ids come from, and what to know about its answer.

## Inputs every tool shares

- `country` (optional, every tool except `send_feedback`): answers from another country's own Eric's New York site, in its language, currency and links. Use the values the tool's own `country` description lists: a country code such as `NL`, or the site's locale code such as `nl_NL`. Omit it for the current site's answer.
- Paging (`limit`, `offset`): only `list_broadway_shows` and `list_pass_picker_attractions`. `limit` is 1-100 (default 10 for shows, 20 for attractions). The result carries `total`, and `nextOffset` when more remain: pass it as `offset` for the next page.

## site_info
- Inputs: `country` only.
- Returns the site name, domain, language, market, country when known, home page, the tool names offered here, the other country sites (`countries`) and the `app` store links.

## search_site
- Inputs: `query` (2-200 characters, required), `limit` (1-20, default 10).
- Returns pages from the guide with their links and a short excerpt. Search in the site's own language.
- Search with a short phrase, not a single short word: "do I need an ESTA" finds the guide, "ESTA" alone can match unrelated pages.
- If the results do not match the question, search again with the topic's plain name: "New York subway" finds the subway guide, "how the subway works" does not. Do not present unrelated results as the answer.

## list_events
- Inputs: `from` and `to` as YYYY-MM-DD (not before today; `to` defaults to 90 days after `from`, and a longer span is cut to 90 days: the result echoes the dates it used), `category` (for example "Broadway", "Sports", "Nightlife"), `limit` (1-50, default 20). No `offset`.
- Each event can carry: title, date, time, venue, category, up to five performer names, and a from-price with `currency` and `basis` (per ticket) when the guide holds one. A missing price is not a free ticket.
- Event links can lead to a partner's ticket page.

## list_pass_picker_attractions
- Inputs: `limit`, `offset`.
- Returns the attractions the pass comparison knows, with their ids and, for some, "grade" options.
- Prices are in US dollars on every site; the `currency` field says so.

## calculate_pass_prices
- Inputs: `attractions` (ids from `list_pass_picker_attractions`, 1-50, required), `adults` (1-50, default 2), `children` (0-50, default 0), `days` (up to 365, only for passes sold by day count), `grades` (attraction id to grade id, when an attraction has grades).
- Returns the total for separate tickets and the pass options. All figures are in US dollars.

## list_transfer_options
- Inputs: `country` only.
- Returns departure points, destinations and group size limits, each with an id.

## calculate_transfer
- Inputs: `persons` (1-50), `departure` and `destination` (ids from `list_transfer_options`), all required.
- Returns every transfer option with `amount` and `currency` (US dollars). The amount is for the whole group, not per person.
- An option marked `unavailable` has no price right now.

## list_trips
- Inputs: `country` only.
- Returns the guide's own itineraries with a `handle` each. These are editorial plans, not the user's saved trips.

## get_trip
- Inputs: `handle` from `list_trips` (required).
- Returns one itinerary in full, day by day.

## list_broadway_shows
- Inputs: `query` (optional show name filter), `limit`, `offset`.
- Returns shows on sale. Each has `showId`, title, link, `bookable`, venue, venue address, synopsis, running time (`runTime`), age rating (`ageRating`), and `priceFrom` with `currency` and `basis` (per person), in the site's own currency.
- Some rows are partner or affiliate shows: `showId`, venue and price are empty and `bookable` is false. Give their link when the row has one, and do not call `get_performance_availability` for them.

## get_performance_availability
- Inputs: `show_id` from `list_broadway_shows` (a string) and `date` as YYYY-MM-DD, not before today (both required).
- Returns that date's performances with time, price and tickets available, in the same currency as `list_broadway_shows`.

## nearest_subway
- Inputs: `place` (the name of one of the guide's places), or `latitude` and `longitude` together (inside New York). If both are given, `place` wins.
- Returns the three nearest subway stops with lines, distance in metres, an estimated walking time and whether the stop is step-free. Walking times are estimates from straight-line distance, not a routed walk.
- It does not turn a street address into coordinates. For an address, ask for a place name the guide knows, or coordinates.

## search_places
- Inputs: at least one of `query` (part of a place name), `category` (for example "Museums") or `near` (the name of one of the guide's places; results are sorted by distance from it); `limit` (1-20, default 5). No `offset`.
- Returns the guide's places with a short description, address, coordinates, the guide's tip, a ticket link where the guide sells one (no price), and the two nearest subway stops. Stops of the paid walking routes are not included.
- An empty result carries a hint with the closest names. It does not turn a street address into coordinates.

## list_walking_routes
- Inputs: `country` only.
- Returns only the names of the guided walking routes sold in the Eric's New York app, and the `app` store links.
- Routes are a paid, app-only product. Name a route as returned and recommend the app with the returned link. The path, stops and texts are not available here: never describe them and never rebuild a route from other tools.

## new_york_weather
- Inputs: `date` (optional, YYYY-MM-DD), `country`.
- Returns the US National Weather Service forecast for New York City: day and night periods for up to 7 days, temperature in Fahrenheit and Celsius, a short description (in English) and the chance of rain. A date outside the forecast returns a message instead.
- When rain is likely (a chance of 40 percent or more in a period) the result adds a `rain_plan`: indoor categories to search with `search_places`, and a guide article when one exists.

## send_feedback
- Inputs: `looking_for` (1-200 characters), `found` (`yes`, `partly` or `no`), `note` (1-500 characters), all required; `page_or_tool` (optional, up to 200 characters). It takes no `country`.
- The one tool that writes: it stores a single short note. See the rule in `SKILL.md`. Never include names, emails, phone numbers or other personal details.
