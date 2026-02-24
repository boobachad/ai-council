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


async def run_group(client: httpx.AsyncClient, member_models: list[str], chairman_model: str, user_prompt: str):
    # Phase 1: independent answers
    tasks = [
        call_llm(client, model, build_leaf_prompt(user_prompt))
        for model in member_models
    ]
    results=await asyncio.gather(*tasks,return_exceptions=True)
    
    leaf_outputs=[]
    successful_leaf_outputs=[]
    for idx,res in enumerate(results):
        model_name=member_models[idx]
        if isinstance(res,Exception):
            leaf_outputs.append(f"{model_name}: No response due to error: {str(res)}")
        else:
            leaf_outputs.append(f"{model_name}:\n{res}")
            successful_leaf_outputs.append(res)

    # Phase 2: deliberation
    deliberation_prompt=build_leaf_deliberation_prompt(user_prompt,successful_leaf_outputs)

    try:
        raw_consensus=await call_llm(client,chairman_model,deliberation_prompt)
        consensus=f"{chairman_model}:\n{raw_consensus}"
    except Exception as e:
        consensus=f"{chairman_model}: No response due to error: {str(e)}"
        
    return {"leaf_outputs":leaf_outputs,"consensus":consensus}
