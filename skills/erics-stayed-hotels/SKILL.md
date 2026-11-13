---
name: erics-stayed-hotels
description: Use when the user asks where to stay in New York, for a hotel in a neighbourhood, or which hotels Eric has stayed in, and the Eric's New York connector is available.
---

# Eric's stayed-at hotels

`search_stayed_hotels` searches Eric's own list of New York hotels he has stayed in, with his one-line verdict. It is not a full hotel search: it has no prices, availability or star ratings.

## Steps

1. Call `search_stayed_hotels` with `query` (part of a hotel name or a neighbourhood, for example "Midtown", up to 100 characters) and `limit` (1-20, default 5). Leave `query` empty to list some of the hotels. Set `country` only as the another-countrys-prices skill describes.
2. Give each hotel's `name` and `neighbourhood`, and its `verdict` word for word when it has one. The verdict is in English: do not rewrite it into praise. `lastStay` is there only for some hotels; give it when it is.
3. When a hotel has a `link`, give it exactly as returned. It is a partner link. When the `note` says so, tell the traveller that Eric earns a commission if they book through the link, at no extra cost to them. A hotel without a `link` has none: do not build one.
4. Never state a price, availability or rating for a hotel. Point to the link for current prices.
5. `total` is the number of hotels that match. When it is higher than the number returned, say that more match and offer a narrower search or a higher `limit`. There is no `offset`.
6. When `hotels` is empty, say Eric's list has no hotel for that search. When the tool answers that the list is not loaded yet, say the list is not available right now. In both cases do not suggest hotels from your own knowledge as if they were on the list.

## Example

This shows only the shape of an answer; always use what the tool returns now.

"Which hotels has Eric stayed in around SoHo?"
- `search_stayed_hotels` with `query: "SoHo"` and `limit: 3` returns `note`, `total` and up to three `hotels`, each with `name` and `neighbourhood`, and `verdict`, `lastStay` and `link` where the list holds them.
- Present each with the verdict as written, then the link and the commission note.
