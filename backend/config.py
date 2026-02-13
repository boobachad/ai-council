import os
from dotenv import load_dotenv

# step1:load env about api keys, stream mode:tokenbytoken or blockbyblock and the db url
load_dotenv()

OPENROUTER_API_KEY=os.getenv("OPENROUTER_API_KEY")
GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")
PERPLEXITY_API_KEY=os.getenv("PERPLEXITY_API_KEY")
DEEPSEEK_API_KEY=os.getenv("DEEPSEEK_API_KEY")#do they have free api key?

OPENROUTER_API_URL="https://openrouter.ai/api/v1/chat/completions"
GEMINI_API_URL=""
PERPLEXITY_API_URL=""
DEEPSEEK_API_URL=""

STREAM_MODE=os.getenv("STREAM_MODE","block") #we need to check this thing called sse
DATABASE_URL=os.getenv("DATABASE_URL","sqlite:///./data/ai_council.db")

# models which the frontend should see
OPENROUTER_MODELS = [
    "google/gemma-3-27b-it:free",
    "liquid/lfm-2.5-1.2b-instruct:free",
    # "cognitivecomputations/dolphin-mistral-24b-venice-edition:free"
    # "provider-name/model-name" #the free-ones will be listed here need to figure out the exact way to list them
]

CHAIRMAN_MODELS = [
    "model-name"
]
