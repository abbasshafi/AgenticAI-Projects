# 🧠 ConceptBuddy – AI Multi-Agent Tutor System

**ConceptBuddy** is a modular, intelligent multi-agent tutor built with the OpenAI Agents SDK and Chainlit. It serves as a virtual tutor capable of answering questions, generating quizzes, and intelligently routing queries to subject-specific agents like Physics, Biology, General Knowledge, and Quiz Generator.

---

## ✨ Features

- ✅ Multi-agent architecture using OpenAI Agents SDK
- 📚 Subject-specialized agents (Physics, Biology, General Knowledge)
- 🧪 Term explanation tool (define_term) using function calling
- 📝 Auto quiz generator with multiple difficulty levels
- 🤖 Intelligent routing via `Triage Agent`
- 🔁 Context-aware conversation using Chainlit session management
- 📦 Streamed token response for real-time user experience

---

## 🏗️ Architecture Overview

             +-------------------+
             |   User Input      |
             +---------+---------+
                       |
             +---------v----------+
             |    Triage Agent    |
             |  (Intent Router)   |
             +----+--+--+--+------+
                  |  |  |  |
    +-------------+  |  |  +----------------+
    |                |  |                   |
+-------v------+ +-------v------+ +-------v---------+
| Physics Agent| | Biology Agent| | GeneralKnowledge|
+--------------+ +--------------+ +-----------------+
|
+-----------------+
| Quiz Generator |
+-----------------+



---

## 🛠️ Setup Instructions

1. **Clone the repository**
```bash
git clone https://github.com/abbasshafi/AgenticAI-Projects.git
cd conceptbuddy

2. Activate UV:
```bash
uv init
uv venv
./activate

Install dependencies:
```bash
uv run openai-agents
uv run chainlit

3. Configure Gemini Api Key:
```bash
GEMINI_API_KEY=your_actual_api_key_here

4. Run the Chainlit app
```bash
uv run chainlit run tutor_agent.py