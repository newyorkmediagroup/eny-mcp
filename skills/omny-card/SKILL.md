---
name: omny-card
description: Use when the user asks about the OMNY card or how to pay for the New York subway and buses before or during a trip, and the Eric's New York connector is available.
---

# OMNY card

Answer from the connector. Do not state fare rules, delivery times or prices from memory.

## Steps

1. Call `get_omny_card_info`.
2. Set `include_prices` to true only when the traveller asks what the card costs. Otherwise leave it out.
3. Set `country` only as the another-countrys-prices skill describes. Otherwise omit it.
4. Report `available` and `what` as returned. The card is a physical card that the site ships to the traveller.
5. Give `url` exactly as returned and say that the purchase happens on that page, never in the chat.
6. List the `options` by name only, as returned. Give `price.amount` with `currency` only when prices were asked for, and say the figures are indicative.
7. When `available` is false, say that this site does not sell the card. Do not point to another seller.

Never invent prices, delivery times or fare rules.

## Example

Shape of an answer only; always use what the tool returns now.

"Can I get an OMNY card for the subway sent to me before my trip?"
- `get_omny_card_info` returned `available` true, a short `what`, and a `url`.
- Say that the site sells the card and ships it, describe it as `what` does, and give the `url` as the page where the purchase is made.
