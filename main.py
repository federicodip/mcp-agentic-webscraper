# main.py
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv
from reporting import write_markdown_report

import asyncio
import os
import argparse
import sys

load_dotenv()

def build_llm(model_id: str, temperature: float = 0.0, max_tokens: int = 1024):
    return ChatAnthropic(model=model_id, temperature=temperature, max_tokens=max_tokens)

def build_server_params(use_mcp: bool):
    if not use_mcp:
        return None
    return StdioServerParameters(
        command="npx",
        env={
            "API_TOKEN": os.getenv("API_TOKEN"),
            "BROWSER_AUTH": os.getenv("BROWSER_AUTH"),
            "WEB_UNLOCKER_ZONE": os.getenv("WEB_UNLOCKER_ZONE"),
        },
        args=["@brightdata/mcp"],
    )

async def run_agent(args):
    # 1) LLM
    llm = build_llm(args.model, args.temperature, args.max_tokens)

    # 2) Tools (optional via MCP)
    tools = []
    server_params = build_server_params(not args.no_mcp)
    if server_params:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                tools = await load_mcp_tools(session)

    # 3) Agent
    agent = create_react_agent(llm, tools=tools)
    messages = []

    # One-shot mode
    if args.question:
        messages.append({"role": "user", "content": args.question})
        agent_response = await agent.ainvoke({"messages": messages})
        ai_message = agent_response["messages"][-1].content
        print(f"Agent: {ai_message}")

        if args.save_report:
            # Convert dicts to the tiny dataclass interface expected by reporter
            msg_objs = [type("Msg", (), m) for m in messages]
            out = write_markdown_report(
                messages=msg_objs,
                ai_reply=ai_message,
                out_path=args.save_report,
                meta={
                    "model": args.model,
                    "used_mcp": not args.no_mcp,
                    "temperature": args.temperature,
                    "max_tokens": args.max_tokens,
                },
            )
            print(f"Saved report to: {out}")
        return

    # Interactive mode
    print("Type 'exit' or 'quit' to end the chat.\n")
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            break
        messages.append({"role": "user", "content": user_input})

        agent_response = await agent.ainvoke({"messages": messages})
        ai_message = agent_response["messages"][-1].content
        print(f"Agent: {ai_message}")

        if args.save_report:
            msg_objs = [type("Msg", (), m) for m in messages]
            out = write_markdown_report(
                messages=msg_objs,
                ai_reply=ai_message,
                out_path=args.save_report,
                meta={
                    "model": args.model,
                    "used_mcp": not args.no_mcp,
                    "temperature": args.temperature,
                    "max_tokens": args.max_tokens,
                },
            )
            print(f"Saved report to: {out}")

def parse_args():
    p = argparse.ArgumentParser(description="MCP Scraper with report export and CLI flags.")
    p.add_argument("--model", default="claude-4-sonnet-20250514", help="Anthropic model id.")
    p.add_argument("--temperature", type=float, default=0.0)
    p.add_argument("--max-tokens", type=int, default=1024)
    p.add_argument("--no-mcp", action="store_true", help="Disable MCP tools.")
    p.add_argument("--question", "-q", help="Run one question non-interactively.")
    p.add_argument("--save-report", help="Save conversation/answer to a Markdown file.")
    return p.parse_args()

def _check_env(no_mcp: bool):
    if not os.getenv("ANTHROPIC_API_KEY"):
        sys.exit("Missing ANTHROPIC_API_KEY in environment.")
    if not no_mcp:
        for k in ["API_TOKEN", "BROWSER_AUTH", "WEB_UNLOCKER_ZONE"]:
            if not os.getenv(k):
                # Not fatal; just a heads-up
                print(f"Warning: env var {k} is not set (MCP may fail).", file=sys.stderr)

def cli():
    args = parse_args()
    _check_env(args.no_mcp)
    asyncio.run(run_agent(args))

if __name__ == "__main__":
    cli()
