# Installing the Eric's New York connector (instructions for AI agents)

Eric's New York is a remote MCP server. There is nothing to clone, build, install or run locally.

- Server URL: `https://ericsnewyork.com/mcp`
- Transport: streamable HTTP (POST only)
- Authentication: none. No sign-in.

## Steps

1. Add `https://ericsnewyork.com/mcp` to the client as a remote MCP server, using the client's own way of adding an HTTP server. A generic configuration:

```json
{
  "mcpServers": {
    "erics-new-york": {
      "type": "http",
      "url": "https://ericsnewyork.com/mcp"
    }
  }
}
```

   Some clients name the transport field or the URL field differently (for example `httpUrl` in Gemini CLI, `streamableHttp` in Cline). Use the client's documented field names for a streamable HTTP server.

2. Restart or reload the client if it does not pick up the server.

## Check that it works

Call the `site_info` tool with no arguments. A working connection returns a site name and a domain.

## What not to do

- Do not add headers or sign-in details. None are needed.
- Do not run local commands, `npm`, `npx`, `pip` or Docker for this server. There is no package.
- Do not use a GET request or a browser to test it. The endpoint accepts POST only.
- Do not book or pay for anything through it. The tools return information and links to pages on the site.
