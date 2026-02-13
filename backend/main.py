from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Request

from pydantic import BaseModel
from . import config
from .database import engine
from . import models

from contextlib import asynccontextmanager
from .services.llm_engine import run_group
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

    # takes the first three models as input
    leaf_models = config.OPENROUTER_MODELS[:3]
    
    try:
        leaf_consensus = await run_group(
                client = client,
                models = leaf_models,
                user_prompt = request.message
            )
        
        return {"response": leaf_consensus}
    
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