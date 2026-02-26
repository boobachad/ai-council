import asyncio
import httpx
import json
from .. import config
OPENROUTER_API_KEY = config.OPENROUTER_API_KEY

async def call_llm(client: httpx.AsyncClient, model: str, messages: list):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "X-Title": "AI Council App",
        "X-Data-Policy": "open"
    }

    payload = {
        "model": model,
        "messages": messages
    }

    response = await client.post(
        config.OPENROUTER_API_URL,
        json=payload,
        headers=headers
    )
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]

def build_leaf_prompt(user_prompt: str):
    return [
        {"role": "system", "content": "You are an expert AI. Answer clearly and correctly."},
        {"role": "user", "content": user_prompt}
    ]

def build_leaf_deliberation_prompt(user_prompt: str, leaf_outputs: list[str]):
    joined = "\n\n".join(
        f"Model {i+1} response:\n{resp}" for i, resp in enumerate(leaf_outputs)
    )

    return [
        {
            "role": "system",
            "content": (
                "You are an AI moderator. You will receive answers from multiple peer models.\n"
                "Your task:\n"
                "1. Identify agreement.\n"
                "2. Resolve conflicts logically.\n"
                "3. Discard weak or incorrect reasoning.\n"
                "4. Produce ONE best consolidated answer.\n"
                "Do NOT introduce new facts."
            )
        },
        {
            "role": "user",
            "content": f"Original question:\n{user_prompt}\n\nPeer responses:\n{joined}"
        }
    ]

async def stream_llm(client: httpx.AsyncClient, model: str, messages: list, node_id: str, queue: asyncio.Queue):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "X-Title": "AI Council App",
        "X-Data-Policy": "open"
    }
    payload = {
        "model": model,
        "messages": messages,
        "stream": True
    }
    
    full_response = ""
    try:
        async with client.stream("POST", config.OPENROUTER_API_URL, json=payload, headers=headers) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data_str = line[len("data: "):]
                    if data_str == "[DONE]":
                        break
                    try:
                        data = json.loads(data_str)
                        if "choices" in data and len(data["choices"]) > 0:
                            delta = data["choices"][0].get("delta", {})
                            if "content" in delta and delta["content"]:
                                content = delta["content"]
                                full_response += content
                                await queue.put({"node": node_id, "chunk": content})
                    except Exception:
                        pass
    except Exception as e:
        error_msg = f"\n[Error: {str(e)}]"
        await queue.put({"node": node_id, "chunk": error_msg})
        return f"Error: {str(e)}"
    
    return full_response


async def stream_group(client: httpx.AsyncClient, member_models: list[str], chairman_model: str, user_prompt: str):
    queue = asyncio.Queue()
    
    async def run_member(model: str, idx: int):
        node_id = f"member-{idx+1}"
        result = await stream_llm(client, model, build_leaf_prompt(user_prompt), node_id, queue)
        return {"model": model, "result": result}
        
    member_tasks = [
        asyncio.create_task(run_member(model, i))
        for i, model in enumerate(member_models)
    ]
    
    while not all(t.done() for t in member_tasks) or not queue.empty():
        try:
            item = await asyncio.wait_for(queue.get(), timeout=0.1)
            yield json.dumps(item) + "\n"
        except asyncio.TimeoutError:
            continue
            
    results = await asyncio.gather(*member_tasks, return_exceptions=True)
    
    successful_leaf_outputs = []
    for res in results:
        if isinstance(res, Exception):
            pass
        elif isinstance(res, dict) and not res["result"].startswith("Error:"):
            successful_leaf_outputs.append(f'{res["model"]}:\n{res["result"]}')

    deliberation_prompt = build_leaf_deliberation_prompt(user_prompt, successful_leaf_outputs)
    
    chairman_task = asyncio.create_task(
        stream_llm(client, chairman_model, deliberation_prompt, "chairman", queue)
    )
    
    while not chairman_task.done() or not queue.empty():
        try:
            item = await asyncio.wait_for(queue.get(), timeout=0.1)
            yield json.dumps(item) + "\n"
        except asyncio.TimeoutError:
            continue
            
    await chairman_task
