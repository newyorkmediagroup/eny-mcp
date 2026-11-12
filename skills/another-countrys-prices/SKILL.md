---
name: another-countrys-prices
description: Use when the traveller is visiting from another country, asks for prices, links or answers in their own currency or language, or asks what another country's Eric's New York site shows, and the Eric's New York connector is available.
---

# Another country's prices

Each country has its own Eric's New York site, with its own language, currency and links. Every tool except `send_feedback` takes an optional `country`.

## Steps

1. Set `country` when the traveller's country or currency differs from this site's, or when they ask for another country's site. Otherwise omit it.
2. Use exactly one accepted value: GB, NL, DE, FR, BR, FI, SE, IT, JP, ES, LATAM, CA, AU, NO, KR or DK. The locale code of the site (for example `nl_NL`) is accepted too.
3. Read `currency` in the answer. Broadway and event prices follow the chosen site. Pass-picker and transfer figures are US dollars on every site.
4. Use the links in that answer; they lead to that country's site.

If the traveller's country is not in the list, answer from this site and say so.

## Example

Figures below are from 12 Nov 2026 and only show the shape of an answer; always use what the tool returns now.

"I am visiting from the Netherlands. What do the Broadway shows cost on the Dutch site?"
- `list_broadway_shows` with `country: "NL"` and `limit: 2` returned The Lion King at 149.41 EUR per person, with a link on newyork.nl.
- Present the price in euros with that link, as indicative.
