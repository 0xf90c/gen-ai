import os, json
from openai import OpenAI
from tools import TOOLS, handle

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM = """
You are a Data Insights assistant.
Rules:
- Never request full database export.
- Use tools to access data.
- Before writing SQL, call get_db_schema unless schema already known.
- Only SELECT queries allowed.
- If user asks destructive operations, refuse and suggest a support ticket.
"""

def _heal_incomplete_tool_calls(messages):
    """
    If the message history contains an assistant tool_call that does not have
    corresponding tool response(s), remove that assistant tool_call message.
    This commonly happens due to Streamlit reruns.
    """
    healed = []
    pending = set()  # tool_call_ids that still need tool responses

    for m in messages:
        role = m.get("role")
        if role == "assistant" and m.get("tool_calls"):
            # register tool calls as pending
            for tc in m["tool_calls"]:
                pending.add(tc["id"])
            healed.append(m)
        elif role == "tool":
            # tool responses resolve a pending call
            tcid = m.get("tool_call_id")
            if tcid in pending:
                pending.remove(tcid)
                healed.append(m)
            else:
                # orphan tool message, keep or drop; keep is fine
                healed.append(m)
        else:
            healed.append(m)

    if pending:
        # remove the last assistant tool_call message that introduced pending calls
        # (simplest safe fix to satisfy API constraints)
        for i in range(len(healed) - 1, -1, -1):
            if healed[i].get("role") == "assistant" and healed[i].get("tool_calls"):
                healed.pop(i)
                break

    return healed

def ask(messages):
    # Ensure dict-based messages + system message
    if not messages or messages[0].get("role") != "system":
        messages = [{"role": "system", "content": SYSTEM}] + [
            m for m in messages if m.get("role") != "system"
        ]
    else:
        messages[0]["content"] = SYSTEM

    # Heal incomplete tool call histories (Streamlit reruns)
    messages = _heal_incomplete_tool_calls(messages)

    while True:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )

        msg = response.choices[0].message

        if msg.tool_calls:
            # Append assistant message with tool calls
            messages.append({
                "role": "assistant",
                "content": msg.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in msg.tool_calls
                ],
            })

            # Execute and append tool results for EACH tool_call_id
            for tc in msg.tool_calls:
                name = tc.function.name
                args = json.loads(tc.function.arguments or "{}")
                result = handle(name, args)

                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "name": name,               # IMPORTANT: include name
                    "content": json.dumps(result),
                })

            # loop again (model will now see tool outputs)
            continue

        # Normal assistant response
        messages.append({
            "role": "assistant",
            "content": msg.content or ""
        })
        return messages