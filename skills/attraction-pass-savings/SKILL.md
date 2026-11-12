---
name: attraction-pass-savings
description: Use when the user asks whether a New York attraction pass or sightseeing pass is worth it, which pass to buy, or how a pass compares with buying separate tickets for the attractions they want to visit.
---

# Attraction pass savings

Answer "is a pass worth it?" with the numbers and the recommendation from the connector, never from memory.

## Steps

1. Find out what the tool needs: which attractions the user wants, how many adults and children, and the number of days if the user gave one (the tool uses it only for passes sold by day count). Ask only for what is missing.
2. Call `list_pass_picker_attractions` and match the user's attractions to ids. If an attraction has `grades` (for example a standard and a premium ticket), pick the one the user described or ask which they want.
3. If an attraction the user named is not in the list, say that the comparison does not cover it and continue with the rest.
4. Call `calculate_pass_prices` once. Use these input names exactly:
   - `attractions`: a list of the id numbers, for example `[285, 257]`. It is a list, not text.
   - `adults` and `children`: whole numbers.
   - `days`: only when the user gave a number of days.
   - `grades`: only for attractions that have grades, as attraction id to grade id.

## Reading the result

The tool returns the total for separate tickets and the pass it recommends, with its reason. The guide's recommendation is the same one its website gives. Report it as returned.

- Give both figures: the total for separate tickets, and the total for the recommended pass.
- Give the tool's reason for its recommendation in plain words. When the recommended pass costs more than separate tickets, the reason is usually that it includes more: say exactly what it adds and what the difference is, for example "for $12 more per person the pass also covers one more attraction".
- State the difference as it is. Call it a saving only when the pass total is lower. When the pass costs more, say that it costs more and what the extra buys.
- Do not replace the tool's recommendation with your own, and do not leave it out. Present it next to the separate-tickets total and let the traveller choose.
- If the tool returns both a cheapest pass and a recommended pass, give the recommended one as the tool does, with its reason, and name the cheapest as the tool reports it. Do not choose between them for the traveller.
- If the tool returns no recommended pass for the selection, say that no pass fits and give the separate-tickets total.

## Currency

Every figure from the pass tools is in US dollars, on every site. Say "US dollars". Do not convert to another currency unless the user asks; if you do, say the conversion is approximate.

## Close

End with the link from the result where the user can check today's price and buy, and say that the figures are indicative.
