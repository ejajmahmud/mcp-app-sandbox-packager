"""CLI for MCP App Sandbox Packager."""
import argparse
import json
from .core import MCPAppPackager


def main():
    parser = argparse.ArgumentParser(description="MCP App Sandbox Packager CLI")
    parser.add_argument("--app-id", default="sample-widget", help="MCP App resource ID")
    parser.add_argument("--html", default="<main><h1>MCP App Ready</h1></main>", help="Body HTML")
    args = parser.parse_args()

    packager = MCPAppPackager(app_id=args.app_id)
    bundle = packager.package(args.html, script="console.log('mcp-app initialized');")
    summary = {k: v for k, v in bundle.items() if k != "html"}
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
