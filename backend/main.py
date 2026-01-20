from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Request

from pydantic import BaseModel
from . import config
from .database import engine
from . import models

from contextlib import asynccontextmanager
import httpx

@asynccontextmanager
async def lifespan(app: FastAPI):
    # starting validation
    if not config.OPENROUTER_API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY not set in environment")
    
    if not config.OPENROUTER_MODELS:
        raise RuntimeError("OPENROUTER_MODELS not set in config")
        
    models.Base.metadata.create_all(bind=engine)

    app.state.http_client=httpx.AsyncClient(timeout=120.0)

    yield

    await app.state.http_client.aclose()

app = FastAPI(title="AI Council", lifespan=lifespan)

class SimpleChatRequest(BaseModel):
    message: str

@app.post("/api/chat")
async def test_chat_msg(request: SimpleChatRequest, req: Request):
    # dont recreate for every request
    client=req.app.state.http_client
    # Use first model from config
    model=config.OPENROUTER_MODELS[0]
    
    headers = {
        "Authorization": f"Bearer {config.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model":model,
        "messages": [{"role":"user","content":request.message}]
    }
    
    try:
        response=await client.post(
                config.OPENROUTER_API_URL,
                headers=headers,
                json=payload
            )
        response.raise_for_status()
        
        data=response.json()
        content=data['choices'][0]['message']['content']
            
        return {"response": content}
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code,detail=f"OpenRouter error: {e.response.text}")
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))


@app.get("/")
def root():
    models={}
    if config.OPENROUTER_API_KEY:
        models["openrouter"]=config.OPENROUTER_MODELS
    if config.GEMINI_API_KEY:
        models["gemini"]=config.GEMINI_MODELS
    if config.PERPLEXITY_API_KEY:
        models["perplexity"]=config.PERPLEXITY_MODELS
    return {
        "status":"ok",
        "message":"ai-council",
        "stream_mode":config.STREAM_MODE,
        "providers":list(models.keys()),
        "models":models
    }

if __name__=="__main__":
    import uvicorn
    uvicorn.run(app,host="0.0.0.0",port=8000)