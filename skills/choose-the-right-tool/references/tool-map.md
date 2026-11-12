# Tool map

One entry per tool: what it needs, where its ids come from, and what to know about its answer.

## site_info
- Inputs: none.
- Returns the site name, domain, language, market, country when known, and home page.

## search_site
- Inputs: `query` (2-200 characters, required), `limit` (1-20, default 10).
- Returns pages from the guide with their links. Search in the site's own language.
- Search with a short phrase, not a single short word: "do I need an ESTA" finds the guide, "ESTA" alone can match unrelated pages.

## list_events
- Inputs: `from` and `to` as YYYY-MM-DD (not before today; `to` defaults to 90 days after `from`), `category` (for example "Broadway", "Sports", "Nightlife"), `limit` (1-50, default 20).
- Event links can lead to a partner's ticket page.

## list_pass_picker_attractions
- Inputs: none.
- Returns the attractions the pass comparison knows, with their ids and, for some, "grade" options.
- Prices are in US dollars on every site; the `currency` field says so.

## calculate_pass_prices
- Inputs: `attractions` (ids from `list_pass_picker_attractions`, 1-50, required), `adults` (default 2), `children` (default 0), `days` (only for passes sold by day count), `grades` (attraction id to grade id, when an attraction has grades).
- Returns the total for separate tickets and the pass options. All figures are in US dollars.

## list_transfer_options
- Inputs: none.
- Returns departure points, destinations and group size limits, each with an id.

## calculate_transfer
- Inputs: `persons` (1-50), `departure` and `destination` (ids from `list_transfer_options`), all required.
- Returns every transfer option with `amount` and `currency`. The amount is for the whole group, not per person.
- An option marked `unavailable` has no price right now.

## list_trips
- Inputs: none.
- Returns the guide's own itineraries with a `handle` each. These are editorial plans, not the user's saved trips.

## get_trip
- Inputs: `handle` from `list_trips` (required).
- Returns one itinerary in full, day by day.

## list_broadway_shows
- Inputs: `query` (optional show name filter).
- Returns shows on sale with their id, title and link. `priceFrom` is in the site's own currency, named by `currency`.

## get_performance_availability
- Inputs: `show_id` from `list_broadway_shows` (a string) and `date` as YYYY-MM-DD, not before today (both required).
- Returns that date's performances with time, price and tickets available, in the same currency as `list_broadway_shows`.
