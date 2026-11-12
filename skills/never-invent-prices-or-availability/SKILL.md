---
name: never-invent-prices-or-availability
description: Use when quoting a price, a currency, ticket availability, a show time or an opening detail for New York from the Eric's New York connector, or when a lookup returned no price or failed.
---

# Never invent prices or availability

A wrong price or a seat that does not exist costs the user money. Report only what the connector returned.

## Prices

- Prices are indicative, not a live quote. Say "from" or "about", and that the page shows today's price.
- Use the `currency` given with the result. Tools differ: pass prices are in US dollars on every site, Broadway prices are in the site's own currency. Never assume one currency for a whole answer.
- Mind the basis. Transfer amounts are for the whole group, not per person. Say which it is.
- Do not add prices from different currencies together.

## No price means no price

When an option is marked `unavailable`, or a price is missing, there is no price right now. Say that it is not available at the moment. Never say it is free, and never show zero.

## Availability

- Report seats and performance times only from `get_performance_availability`, for the date that was asked.
- No date from the user means no availability claim: ask for the date first.
- Availability changes quickly. Say when you looked it up if the conversation continues for long.

## Never guess

Do not guess ids, show names, dates, times, opening hours or addresses. If the connector did not return it, say you do not have it and offer the page where the user can check.

## When a lookup fails

Read the error message. It usually lists the valid values. Fix the input and try once. If it fails again, tell the user what could not be looked up and give the link to the relevant page instead of filling the gap.
