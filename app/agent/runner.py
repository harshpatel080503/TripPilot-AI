"""Single-role agentic loop — one API conversation until stop_reason != tool_use."""
import json
import logging
import time
import uuid
from typing import Optional

from openai import AsyncOpenAI

from app import db
from .config import MODEL, MAX_TOKENS, ROLE_TOOL_SERVERS
from .executor import ToolExecutor
from .prompts import AGENT_PROMPTS

logger = logging.getLogger(__name__)

class MockToolCall:
    """A simple wrapper to adapt OpenAI tool calls for the ToolExecutor which expects .name and .input"""
    def __init__(self, name: str, input_args: dict):
        self.name = name
        self.input = input_args

class AgentRunner:
    def __init__(self, client: AsyncOpenAI, executor: ToolExecutor):
        self._client = client
        self._executor = executor

    async def run(
        self,
        role: str,
        message: str,
        max_turns: int,
        run_id: str,
        agent_call_id: str,
    ) -> str:
        model = MODEL[role]
        max_tokens = MAX_TOKENS[role]
        system_prompt = AGENT_PROMPTS[role]

        history = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]

        available = self._executor.filter_tools(role, ROLE_TOOL_SERVERS)
        openai_tools = [
            {
                "type": "function",
                "function": {
                    "name": t["name"],
                    "description": t["description"],
                    "parameters": {
                        "type": "object",
                        "properties": t.get("inputSchema", {}).get("properties", {}),
                        "required": t.get("inputSchema", {}).get("required", []),
                    },
                }
            }
            for t in available
        ]

        db.create_agent_call(agent_call_id, run_id, role, model)
        call_start = time.monotonic()
        total_input = total_output = total_cache_read = total_cache_write = tool_count = 0
        final_text = ""

        logger.info("  [%s] starting — model: %s  max_turns: %d  tools: %d",
                    role, model, max_turns, len(openai_tools))

        for turn in range(max_turns):
            turn_start = time.monotonic()
            kwargs: dict = dict(model=model, max_tokens=max_tokens, messages=history, temperature=0.7)
            if openai_tools:
                kwargs["tools"] = openai_tools
            
            if role in ["planner", "aggregator"]:
                kwargs["response_format"] = {"type": "json_object"}

            response = await self._client.chat.completions.create(**kwargs)
            message_obj = response.choices[0].message
            
            usage = getattr(response, "usage", None)
            if usage:
                total_input       += getattr(usage, "prompt_tokens", 0)
                total_output      += getattr(usage, "completion_tokens", 0)

            history.append(message_obj.model_dump(exclude_unset=True))

            if not message_obj.tool_calls:
                final_text = message_obj.content or ""
                if role == "pricer" and "## 🚌 Transport Outbound" not in final_text and turn < max_turns - 1:
                    logger.info("  [pricer] turn %d: no tool calls but final markdown not found. Forcing continuation.", turn)
                    history.append({"role": "user", "content": "You paused without issuing tool calls for the remaining steps, and you haven't output the final markdown results. Please issue the tool calls for the remaining steps now."})
                    continue
                    
                logger.info("  [%s] turn %d/%d → STOP (%s)  %.1fs  out_tokens: %d",
                            role, turn + 1, max_turns, response.choices[0].finish_reason,
                            time.monotonic() - turn_start,
                            getattr(usage, "completion_tokens", 0))
                break

            turn_calls = message_obj.tool_calls or []
            tool_count += len(turn_calls)
            call_names = [tc.function.name for tc in turn_calls]
            logger.info("  [%s] turn %d/%d → tool_use  calls: %s  %.1fs",
                        role, turn + 1, max_turns, call_names,
                        time.monotonic() - turn_start)

            import asyncio
            
            async def exec_tool(tc):
                try:
                    args = json.loads(tc.function.arguments)
                except json.JSONDecodeError:
                    args = {}
                executor_tc = MockToolCall(tc.function.name, args)
                res = await self._executor.execute(executor_tc, role, agent_call_id, run_id)
                return {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": res,
                }
            
            tool_results = await asyncio.gather(*(exec_tool(tc) for tc in turn_calls))
            history.extend(tool_results)
        else:
            logger.warning("  [%s] REACHED TURN LIMIT (%d)", role, max_turns)
            final_text = "Agent reached turn limit."

        duration_ms = int((time.monotonic() - call_start) * 1000)
        db.complete_agent_call(
            agent_call_id, duration_ms,
            total_input, total_output, total_cache_read, total_cache_write,
            tool_count, final_text,
        )
        logger.info("  [%s] done — %dms  in:%d  out:%d  cache_read:%d  tools_called:%d  output:%d chars",
                    role, duration_ms, total_input, total_output,
                    total_cache_read, tool_count, len(final_text))
        return final_text