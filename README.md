# TripPilot AI ✈️

> An autonomous, multi-agent travel planner that performs live web scraping to build accurate, real-time trip dossiers.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![React](https://img.shields.io/badge/React-18-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)
![Playwright](https://img.shields.io/badge/Playwright-MCP-orange.svg)
![License](https://img.shields.io/badge/License-MIT-purple.svg)

## 🚀 Overview
TripPilot AI is a fully autonomous, multi-agent AI system designed to eliminate the friction of travel planning. By utilizing a pipeline of specialized agents equipped with browser manipulation tools (via the Model Context Protocol), the system conducts live Google searches in real-time. It retrieves live flight prices, hotel rates, and activity costs, then uses a secure calculator to generate a multi-tier budget and a comprehensive JSON travel dossier, all streamed live to a responsive React frontend.

## 🎯 Problem
Planning a trip manually requires opening dozens of tabs, comparing flights across different dates, checking Airbnb prices vs. hotel rates, and manually calculating budgets for different tiers (economy vs. luxury). Traditional AI chatbots hallucinate prices or provide outdated information because they lack access to the live web and cannot perform rigorous, step-by-step arithmetic.

## 💡 Why This Approach?
TripPilot AI solves this by employing a deterministic **Multi-Agent Pipeline**. Instead of asking one model to "plan a trip," the task is divided:
1. A **Planner** structures the route.
2. A **Pricer** uses Playwright to physically scrape Google for live prices in parallel.
3. A **Budget Analyst** uses an isolated calculator tool to compute costs without arithmetic hallucinations.
4. An **Aggregator** forces the final output into a strict JSON schema.

This modular architecture guarantees live, hallucination-free data and allows for aggressive parallelization, dropping search times from minutes to seconds.

## ✨ Key Capabilities
* **Live Web Scraping:** Uses the Model Context Protocol (MCP) to drive a Playwright browser, extracting real-time prices directly from Google Search AI Overviews.
* **Parallel Tool Execution:** The Pricer agent dispatches all search queries (flights, hotels, activities) concurrently using asynchronous execution, drastically reducing wait times.
* **Strict Structured Outputs:** System guardrails enforce 100% compliant JSON responses, preventing frontend crashes from conversational filler.
* **Persistent Memory & Caching:** A SQLite-backed caching layer intercepts duplicate searches, returning historical JSON instantly.
* **Live UI Streaming:** Uses Server-Sent Events (SSE) to stream the AI's internal thoughts and active tasks (e.g., *"🔍 Scouting live prices..."*) directly to the user interface.
* **Global Support:** Dynamically routes deep-links for global transport operators (Eurostar, Kayak, FlixBus) for any city in the world.

## 🏗️ Architecture
The system follows a classic decoupled client-server architecture:
* **Frontend:** React (Vite) Single Page Application (SPA).
* **Backend:** FastAPI asynchronous server.
* **Database:** SQLite (WAL mode) for caching and agent trajectory tracking.
* **AI Orchestration:** Custom `AgentRunner` leveraging the OpenAI standard API format to coordinate local or cloud LLMs.

## 🔄 End-to-End Workflow
1. User submits a request (e.g., "Toronto to Paris, 2 people, 7 days") via the React UI.
2. FastAPI intercepts the request and checks the SQLite cache. If a match exists, it returns immediately.
3. **Phase 1 (Planner):** Generates a JSON manifest of required transport and accommodation deep-links.
4. **Phase 2 (Pricer):** Uses MCP and Playwright to launch a headless Chromium instance, scraping Google for live prices simultaneously.
5. **Phase 3 (Budget):** Takes the scraped unstructured text and uses a Python calculator tool to compute Economy, Mid-Range, and Comfort totals.
6. **Phase 4 (Aggregator):** Compiles the context, raw prices, and budget into a highly structured JSON document.
7. The JSON is decoded and beautifully rendered by the React frontend.

## 🧠 AI / ML Methodology

### Model
Configured to use **gpt-oss:120b-cloud** (or any OpenAI-compatible endpoint). The backend isolates roles, assigning varying token limits and temperatures based on the phase.

### Retrieval
The system uses **Live Tool Retrieval** rather than static RAG. It actively fetches its own context dynamically via live Google Searches.

### Agents
Uses a sequential pipeline of specialized personas: `Planner`, `Pricer`, `Budget`, and `Aggregator`.

### Memory
Short-term memory is managed via an active conversational history array. Long-term memory is persisted in `travel_runs.db` (SQLite), storing input prompts, JSON outputs, and individual agent trajectories.

### Tools
Integrated via the **Model Context Protocol (MCP)**:
* `playwright-mcp`: For `browser_navigate` and `browser_evaluate`.
* `calculator-mcp-server`: For precise budget arithmetic.

### Prompting
Extensive prompt engineering is utilized to format outputs. The Pricer prompt explicitly commands parallel tool execution (e.g., *"You MUST issue ALL tool calls for ALL 6 steps simultaneously..."*).

### Guardrails
* **JSON Forcing:** `response_format={"type": "json_object"}` is enforced.
* **Conversational Pauses:** The execution runner detects if the LLM pauses midway without issuing tools, actively prompting it to continue to prevent stalled states.

## 📊 Dataset / Knowledge Sources
TripPilot AI relies on the open internet for its ground truth. It synthesizes data from:
* Google Search AI Overviews
* Kayak
* Airbnb
* Global transit operators (VIA Rail, Eurostar, Flixbus)

## ⚙️ Tech Stack
* **Language:** Python 3.11+, JavaScript (ES6+)
* **Backend:** FastAPI, Uvicorn, SQLite
* **Frontend:** React, Vite
* **AI Integration:** OpenAI Python SDK, Model Context Protocol (MCP)
* **Scraping:** Playwright

## 📁 Repository Structure
```text
TripPilot AI/
├── app/
│   ├── api.py              # FastAPI application & SSE streaming
│   ├── db.py               # SQLite caching and state management
│   └── agent/
│       ├── pipeline.py     # 4-phase orchestration pipeline
│       ├── runner.py       # Custom LLM execution loop
│       ├── executor.py     # MCP tool parsing & execution
│       ├── prompts.py      # System instructions
│       └── config.py       # Model & MCP server configs
├── frontend/
│   ├── src/
│   │   ├── App.jsx         # Main React SPA & SSE parser
│   │   └── TripResult.jsx  # Travel dossier UI renderer
│   └── package.json
├── travel_runs.db          # Persistent SQLite database
├── .env                    # Secure API keys
└── README.md
```

## 🚀 Installation

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/TripPilot-AI.git
cd "TripPilot AI"
```

2. **Install Backend Dependencies:**
Ensure you have `uv` installed, then set up the environment.
```bash
uv pip install -r requirements.txt
```

3. **Install Frontend Dependencies:**
```bash
cd frontend
npm install
```

4. **Install Playwright MCP:**
```bash
npx -y @playwright/mcp@0.0.83 install-browser chrome-for-testing
```

## 🔐 Configuration
Create a `.env` file in the root directory and add your LLM API Key:
```env
OLLAMA_API_KEY=your_secure_api_key_here
```

## ▶️ Running the System

Start the backend server (from the root directory):
```bash
uv run uvicorn app.api:app --reload --log-level info
```

Start the frontend development server (from the `frontend` directory):
```bash
npm run dev
```
Navigate to `http://localhost:5173` to start planning!

## 🔌 API

### `POST /api/chat/stream`
Accepts a travel request and streams Server-Sent Events (SSE) back to the client.

**Request:**
```json
{
  "message": "New York to Paris, May 15 to May 22, 2 people",
  "transport_mode": "any"
}
```

**Response (SSE Stream):**
```text
data: {"type": "session", "session_id": "1234-abcd"}
data: {"type": "phase", "phase": "🗺️ Planning your route..."}
data: {"type": "phase", "phase": "🔍 Scouting live prices..."}
data: {"type": "result", "reply": "{...full JSON dossier...}"}
```

## 💻 Example
**User Input:** "Tokyo to Kyoto, 2 people, economy budget"
**System Action:**
1. Plans the Shinkansen route.
2. Scrapes Google for live Bullet Train prices and Kyoto ryokan/hotel prices.
3. Calculates the total cost for 2 people.
4. Streams the finalized budget, itinerary, and booking links to the UI.

## 📈 Evaluation
The system is evaluated based on **Scraping Success Rate** and **JSON Conformance**. 
By enforcing parallel tool calling and stripping conversational filler, the failure rate of the pipeline has been reduced to < 5%. 

## 🧪 Experiments / Ablations
* **Sequential vs. Parallel Tools:** Initially, the Pricer searched for flights, waited, and then searched for hotels. By updating the prompt to force the model to issue 6+ tool calls simultaneously, total execution time plummeted from ~90 seconds to ~25 seconds.
* **Native Playwright vs. MCP:** Utilizing MCP abstracts the scraping logic, ensuring the LLM relies on robust, community-tested browser commands rather than writing its own fragile scraping scripts.

## ⏱️ Performance
* **Cold Start (No Cache):** 25 - 40 seconds (includes live web scraping).
* **Warm Start (Cached):** < 0.5 seconds.

## 🖥️ Demo
*(Insert link to video or GIF demonstrating the Live SSE streaming and UI population)*

## 🧩 Engineering Decisions
* **SQLite over In-Memory:** Using a persistent SQLite WAL database ensures that previous trips are permanently cached across server restarts, acting as both an optimization layer and an audit trail for agent behavior.
* **SSE over WebSockets:** Server-Sent Events were chosen over WebSockets because the interaction is purely unidirectional (server pushing updates to the client) after the initial request, minimizing overhead.

## ⚠️ Limitations
* Google Search DOM structures change frequently. If the AI Overview format changes, the extraction instructions in the `Pricer` prompt may require slight tuning.
* Extremely obscure routing may cause the Playwright agent to return "No live data" if Google cannot confidently surface a price in its top snippets.

## 🔮 Future Work
* **User Authentication:** Allow users to save their trips to individual profiles.
* **Automated Booking:** Integrate with booking APIs (e.g., Amadeus) to transition from a "planning" agent to an "action" agent that securely books the trip.
* **Agentic Retry Loops:** Implement a reflection agent that grades the output of the Pricer; if prices are missing, it reformulates the query and tries again before passing data to the Budget agent.

## 📚 References
* [Model Context Protocol (MCP)](https://github.com/modelcontextprotocol)
* [Playwright](https://playwright.dev/)
* [FastAPI](https://fastapi.tiangolo.com/)

## 📜 Citation
If you use TripPilot AI in your research or project, please cite:
```text
@software{TripPilotAI2026,
  author = {Your Name},
  title = {TripPilot AI: Autonomous Multi-Agent Travel Planner},
  year = {2026},
  publisher = {GitHub},
  url = {https://github.com/yourusername/TripPilot-AI}
}
```

## 🤝 Contributing
Contributions are welcome! Please fork the repository and submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 📄 License
This project is licensed under the MIT License. See the `LICENSE` file for details.

## 👤 Author
Developed by **Harsh Patel**.