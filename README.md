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

## What you can ask

Examples for a first or second visit to New York. The connector answers from the guide and links to the page each answer came from.

- "We are two adults and two children for five days. Is an attraction pass cheaper than separate tickets for the Empire State Building, the Statue of Liberty and the Top of the Rock?"
- "How do we get from JFK to a hotel in Manhattan, and what does it cost for a group of four?"
- "Which Broadway shows have seats on 14 March, and at what prices?"
- "What is on in New York between 10 and 14 March?"
- "Show me a ready-made itinerary for a first visit."
- "Do I need an ESTA for New York?"
- "Find Eric's guide to how the subway works."

## What it does not do

Nothing is booked, bought or paid for through the connector. Claude gives you the link to the page on our site where you can check today's price and book. No account, key or sign-in is needed.

## Install

The connector is a remote server at `https://ericsnewyork.com/mcp` (streamable HTTP, POST only). It needs no sign-in or key, and nothing is installed or run locally.

| Client | How to add it |
| --- | --- |
| Claude (web and desktop) | Open the [prefilled link](https://claude.ai/customize/connectors?modal=add-custom-connector&connectorName=Eric%27s%20New%20York&connectorUrl=https%3A%2F%2Fericsnewyork.com%2Fmcp), or go to Customize > Connectors > Add custom connector and enter `https://ericsnewyork.com/mcp`. Directory listing coming soon. |
| Claude Code (plugin) | `claude plugin marketplace add newyorkmediagroup/eny-mcp`, then `/plugin install erics-new-york-mcp@eny-mcp`. This also installs the skills. |
| Claude Code (connector only) | `claude mcp add --transport http erics-new-york https://ericsnewyork.com/mcp` |
| ChatGPT | Directory listing coming soon. Meanwhile, OpenAI documents custom MCP servers at chatgpt.com/plugins (plus button, Add custom MCP server, public HTTPS endpoint). OpenAI's help page states that custom MCP server connections are available for ChatGPT Business and Enterprise/Edu customers on ChatGPT web, and that account and workspace policies apply. See [OpenAI's help article](https://help.openai.com/en/articles/12584461-connecting-custom-mcp-servers-in-chatgpt). |
| Cursor | Add to `.cursor/mcp.json` (project) or `~/.cursor/mcp.json` (global): `{"mcpServers": {"erics-new-york": {"url": "https://ericsnewyork.com/mcp"}}}` |
| Cline | In the MCP Servers panel open Remote Servers, enter the URL and choose Streamable HTTP. Or add to `cline_mcp_settings.json`: `{"mcpServers": {"erics-new-york": {"type": "streamableHttp", "url": "https://ericsnewyork.com/mcp"}}}` |
| Gemini CLI | `gemini mcp add --transport http erics-new-york https://ericsnewyork.com/mcp` |
| VS Code (GitHub Copilot) | `code --add-mcp '{"name":"erics-new-york","type":"http","url":"https://ericsnewyork.com/mcp"}'`, or run MCP: Add Server from the Command Palette and choose HTTP. |
| Any other client | Add `https://ericsnewyork.com/mcp` as a remote MCP server (HTTP). |

To check it works, ask the assistant to call `site_info`. It should return the site name and domain.

Files in this repository:

- `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`: the Claude Code plugin and its marketplace.
- `.mcp.json`: the connector entry in the format Claude Code and VS Code Copilot read from a project root. Other clients use their own file, shown above.
- `llms-install.md`: install steps written for an AI agent.

## Your data

Your questions are sent to the connector at `https://ericsnewyork.com/mcp`, which looks them up in the guide and returns the results. The plugin itself runs no code and stores nothing. See the privacy policy below.

## Prices

Prices returned by the connector are indicative, not a live quote. The final price is the one shown on the linked page.

## Links

- How to connect: https://ericsnewyork.com/connect/
- Privacy policy: https://www.newyork.co.uk/privacy-policy/
- Connector address: `https://ericsnewyork.com/mcp`

## Contact and community

Would you like advice from a person? Email eric@ericsnewyork.com.

- Facebook: https://facebook.com/newyork
- Instagram: https://instagram.com/visitnewyork
- YouTube: https://www.youtube.com/@EricsNewYork
- Eric's New York app for iPhone: https://apps.apple.com/app/erics-new-york/id1129643452
- Eric's New York app for Android: https://play.google.com/store/apps/details?id=com.ericsnewyork

## Licence

Copyright New York Media Group B.V. All rights reserved. See `LICENSE`.
