import asyncio
import httpx
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


async def run_group(client: httpx.AsyncClient, models: list[str], user_prompt: str):
    # Phase 1: independent answers
    tasks = [
        call_llm(client, model, build_leaf_prompt(user_prompt))
        for model in models
    ]
    leaf_outputs = await asyncio.gather(*tasks)

    # Phase 2: deliberation
    deliberation_prompt = build_leaf_deliberation_prompt(user_prompt, leaf_outputs)
    deliberator_model = models[0]

    consensus = await call_llm(client, deliberator_model, deliberation_prompt)
    return {"leaf_outputs":leaf_outputs,"consensus":consensus}
