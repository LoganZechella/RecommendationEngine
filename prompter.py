import openai
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import dotenv
import os

dotenv.load_dotenv()

app = FastAPI()

# Define Pydantic models for input and output data
class UserProfile(BaseModel):
    age: int
    interests: List[str]
    location: str

class Query(BaseModel):
    event_type: str
    date: str
    location: str

class GeneratePromptRequest(BaseModel):
    user_profile: UserProfile
    query: Query

class GeneratePromptResponse(BaseModel):
    prompt: str

class RefinePromptRequest(BaseModel):
    prompt: str
    feedback: str

class RefinePromptResponse(BaseModel):
    refined_prompt: str

# Initialize the OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Define the endpoint to generate prompts
@app.post("/generate-prompt", response_model=GeneratePromptResponse)
async def generate_prompt(request: GeneratePromptRequest):
    prompt = await generate_prompt_from_input(request.user_profile, request.query)
    return GeneratePromptResponse(prompt=prompt)

# Define the endpoint to refine prompts
@app.post("/refine-prompt", response_model=RefinePromptResponse)
async def refine_prompt(request: RefinePromptRequest):
    refined_prompt = await refine_existing_prompt(request.prompt, request.feedback)
    return RefinePromptResponse(refined_prompt=refined_prompt)

# Helper functions to generate and refine prompts
async def generate_prompt_from_input(user_profile: UserProfile, query: Query) -> str:
    prompt_text = (
        f"Generate a list of events in {user_profile.location} for individuals aged {user_profile.age} with interests in "
        f"{', '.join(user_profile.interests)}. The events should include {query.event_type} scheduled for {query.date}. "
        f"Provide details such as event name, date, time, location, and a brief description."
    )
    
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt_text,
        max_tokens=150
    )
    return response.choices[0].text.strip()

async def refine_existing_prompt(prompt: str, feedback: str) -> str:
    prompt_text = (
        f"Refine the following prompt based on the feedback provided: {prompt}\nFeedback: {feedback}"
    )
    
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt_text,
        max_tokens=150
    )
    return response.choices[0].text.strip()

# Run the FastAPI server using Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)