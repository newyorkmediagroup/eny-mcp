# Eric's New York

Eric's New York is an independent New York City travel guide by a local. This plugin teaches Claude how to use the Eric's New York connector well when you plan a trip to New York City.

## What it does

With the connector, Claude can look things up in the guide for you:

- Broadway shows that are on sale, and which performances have seats on a given date
- Attraction passes: which attractions each pass covers, and how a pass compares with buying separate tickets for your party
- Airport transfers: the options between the airports and your destination, with indicative prices for your group
- Events in New York by date and category
- Ready-made trip itineraries
- Anything else in the guide, through site search

The skills in this plugin tell Claude which tool to use for which question, how to present the guide's attraction pass recommendation next to the price of separate tickets, to name and link the page every answer came from, and never to invent a price or availability.

## What it does not do

Nothing is booked, bought or paid for through the connector. Claude gives you the link to the page on our site where you can check today's price and book. No account, key or sign-in is needed.

## Your data

Your questions are sent to the connector at `https://ericsnewyork.com/mcp`, which looks them up in the guide and returns the results. The plugin itself runs no code and stores nothing. See the privacy policy below.

## Prices

Prices returned by the connector are indicative, not a live quote. The final price is the one shown on the linked page.

## Links

- How to connect: https://ericsnewyork.com/connect/
- Privacy policy: https://www.newyork.co.uk/privacy-policy/
- Connector address: `https://ericsnewyork.com/mcp`

## Licence

Copyright New York Media Group B.V. All rights reserved. See `LICENSE`.
