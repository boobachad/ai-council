# Pointers

1. **persona** = council members or chairman, **models** ≠ council members or chairman
2. debate is an additional feature from the getgo its supposed to be a simple chat thing
3. each persona will have name, prompt, model
4. models to use:
    - Why Open Router?
    Using Open Router coz it will provide all the freely available models at one place no need to scrible around.
    - we will use open router also in addition to other providers. this is good but for chairmen we need a model which has great context since when reaching the final phase/stage there will be so much content that the free models wont be able to handle it well.

## Contribution

1. clone this repo and go to root(repo/foldername) folder search how?
2. run `uv sync` to install libraries
3. `uv run python -m backend.main`

---

# What is Context Size of an LLM?
It is the amount of token an LLM can process at once.
What is a Token?
Token is a Unit used to measure the context size of an LLM. 
Numerically 1 token approx to 4 chars.
Why do we need to keep the context size of an LLM in mind for our project?
because the chairman is going to have all the responses of the members and through this responses
the chairman is going to give the final response to the user.
What will the context that our chairman and other members are gonna have?
1. Current question asked.
2. Previous Messages in the conversation
3. System and Developer instructions
4. Any pasted text , code or document.
5. The model's previous replies.
The optimal way to save the previous conversation without wasting enough tokens is that we'll store the summary of the previous conversation.
## My Opinion.
Don't know that this will change the concept of the project or not but what im thinging is that what if we have a heirarchy of all these models?
Like the leaf models will pass the response to the parents the parents are gonna act as chairman for its decendents and then the parents will curate
an response based on its child and pass the reply to it's parents and finally the root model gives the response to the user.
How is this useful.
each parent only have to store the conversation of its own and its two childrens. 
