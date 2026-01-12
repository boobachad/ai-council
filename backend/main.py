from fastapi import FastAPI
from . import config
from .database import engine
from . import models

models.Base.metadata.create_all(bind=engine)

app=FastAPI(title="AI Council")

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