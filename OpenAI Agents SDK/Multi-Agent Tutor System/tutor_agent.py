import os, json
import asyncio
from typing import List
from agents import Agent, Runner, OpenAIChatCompletionsModel,function_tool,RunConfig,handoff,FunctionTool,function_tool
from openai import AsyncOpenAI
from dotenv import load_dotenv, find_dotenv
from openai.types.responses import ResponseTextDeltaEvent
from pydantic import BaseModel
import chainlit as cl

load_dotenv()
GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set. Please ensure it is defined in your .env file.")

client= AsyncOpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
    
model=OpenAIChatCompletionsModel(model="gemini-2.0-flash",openai_client=client)

config=RunConfig(
    model=model,
    tracing_disabled=True
)

# class QuizItem(BaseModel):
#     question: str
#     options: List[str]
#     correct_option: str

# Function tool
@function_tool
def define_term(term: str) -> str:
    """
    Explains a scientific or technical term in simple language.
    
    Args:
        term (str): The term to define.
    
    Returns:
        str: A plain-English explanation of the term.
        
    Output Style:
        - Start with: "'{term}' is a ..."
        - Use analogies or examples if possible.
        - End with: "Was that simple enough for you?"
    """
    return f"'{term}' is a technical or scientific term. In simple terms, it refers to a concept or object used in that field. Please refine the term if a more specific answer is needed."

# Agents
general_knowledge_agent= Agent(
    name="General Knowledge Agent",
    instructions="""
    You are a helpful and knowledgeable assistant specialized in general knowledge. 
    Answer questions clearly and concisely, covering a wide range of topics including history, geography, science, current affairs, and world facts.

    When the user asks something vague, politely ask for clarification.
    Provide examples or analogies when helpful, and offer extra interesting facts if the user seems curious.
    Always keep the tone friendly and informative.
    """,
    model=model,
)

biology_agent= Agent(
    name="Biology Agent",
    instructions="""
    You are a biology subject expert who explains complex biological concepts in a simple, engaging, and student-friendly way.
    
    Your main goals:
    - Break down biological topics into easy-to-understand explanations using real-world analogies.
    - Highlight important terms and processes.
    - Use bullet points, numbered lists, or step-by-step logic where helpful.
    - If the student says "explain in simpler terms" or seems confused by a term, identify that key term and call the `define_term` tool.
    
    Always confirm understanding at the end by asking something like: "Was that clearer?" or "Would you like a visual or example?"
    """,
    model=model,
    tools=[define_term],
)

physics_agent= Agent(
    name="Physics Agent",
    instructions="""
    You are a physics subject expert who teaches complex concepts in an easy and engaging way, tailored for students.

    Your responsibilities:
    - Explain physics topics clearly, using simple language and real-world analogies.
    - Format your answers with clear structure: a short summary, followed by detailed explanation and optionally bullet points.
    - If the student asks something like "explain in simpler terms", identify the confusing word or concept and use the 'define_term' tool for it.
    
    Always end your explanation with a follow-up like: "Was that clearer?" or "Want to go deeper?"
    """,
    model=model,
    tools=[define_term],
)

quiz_agent= Agent(
    name="Quiz Agent",
    instructions="""
    You are a quiz generation assistant. Your job is to generate ** multiple-choice questions** (MCQs) based on the given topic.

    ✅ Format for each question:
    - `question`: A clear and concise question.
    - `options`: A list of 4 distinct choices (A-D), only one of which is correct.
    - `correct_option`: One of the 4 options that is correct.

    ✅ Guidelines:
    - Cover a mix of difficulty levels: 2 easy, 2 medium, 1 hard.
    - Avoid repetition and ensure conceptual diversity within the 5 questions.
    - Keep questions relevant to the topic and educational in tone.

    End your response by asking: “Would you like to try another topic?”
    """,
    model=model,
    # output_type=Qbot,
)

triage_agent = Agent(
    name="Triage Agent",
    instructions="""
    Your job is to analyze user input and determine which specialized agent should handle the request. Route based on subject or intent.

    🎯 Routing Guidelines:
    - ➤ Route to **Physics Agent** if input includes physics-related terms like 'force', 'energy', 'motion', 'gravity', 'velocity', or is a direct physics question.
    - ➤ Route to **Biology Agent** if the message includes biology terms such as 'cell', 'DNA', 'organism', 'photosynthesis', 'ecology', etc.
    - ➤ Route to **Quiz Agent** if the user asks to 'generate a quiz', 'create questions', 'test me', or anything related to quiz/test creation.
    - ➤ Route to **General Knowledge Agent** for questions that are not clearly related to physics, biology, or quizzes—e.g., history, facts, geography, etc.

    🔁 If the input is ambiguous or unclear:
    - Ask a clarifying question to understand the topic or subject better.
    - Do NOT answer the question directly—just clarify or route.

    ⚙️ If a routed agent has tools available (e.g., `define_term`), allow them to invoke tools if needed.
    """,
    handoffs=[quiz_agent, biology_agent, physics_agent,general_knowledge_agent]
)

@cl.on_chat_start
async def start():
    cl.user_session.set("History", [])
    await cl.Message(content="Hello I am Tutor Agent ConceptBuddy, how can I help you today?").send()

@cl.on_message
async def handle_message(message: cl.Message):
    history = cl.user_session.get("History") or []
    history.append({"role": "user", "content": message.content})

    # Initialize a streaming Chainlit message
    stream_msg = cl.Message(content="")
    await stream_msg.send()

    result = Runner.run_streamed(
        starting_agent=triage_agent,
        run_config=config,
        input=history
    )

    full_reply = ""

    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            token = event.data.delta
            full_reply += token
            await stream_msg.stream_token(token)

    history.append({"role": "assistant", "content": full_reply})
    cl.user_session.set("History", history)

# @cl.on_message
# async def handle_message(message: cl.Message):
#     history = cl.user_session.get("History") or []
#     history.append({"role": "user", "content": message.content})

#     # Initialize a streaming Chainlit message
#     stream_msg = cl.Message(content="")
#     await stream_msg.send()

#     try:
#         result = Runner.run_streamed(
#             starting_agent=triage_agent,
#             run_config=config,
#             input=history
#         )

#         full_reply = ""

#         async for event in result.stream_events():
#             if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
#                 token = event.data.delta
#                 full_reply += token
#                 await stream_msg.stream_token(token)

        

#         history.append({"role": "assistant", "content": full_reply})
#         cl.user_session.set("History", history)

#     except Exception as e:
#         # await stream_msg.update(content="⚠️ An error occurred while processing your message. Please try again.")
#         print("Error during agent response streaming:", e)


@cl.on_chat_end
async def on_chat_end():
    history = cl.user_session.get("History") or ['no data']
    with open("chat_history.json", "w") as f:
        json.dump(history, f, indent=2)
    print("Chat history saved.")


# Async execution wrapper
# async def main():
#     query = input("Enter the query: ")
#     result = await Runner.run(quiz_agent, input=query)
#     print(result.final_output)

# # Run
# asyncio.run(main())


