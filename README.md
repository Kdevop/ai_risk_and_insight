# 🏦 Banking Analytics Assistant
A lightweight natural‑language analytics tool that turns user questions into SQL queries, executes them, and returns clear insights through a clean chat‑style UI.

## 🚀 Overview
Users can ask questions like:
- List the accounts for a customer
- Show monthly spend
- View alerts
- Summarise financial activity

The system:
1. Interprets the question  
2. Runs the correct SQL tool  
3. Returns SQL + results  
4. Generates a readable explanation  
5. Displays everything in a modern UI  

## 🧠 Architecture
Frontend:
- HTML/CSS/JS (no frameworks)
- Chat interface with Markdown rendering
- Dark mode toggle
- Thinking animation
- SQL show/hide panel
- Auto‑generated results table

Backend:
- Python + Flask
- Agent loop with session history
- Tool‑driven SQL execution
- SQLite database (banking.db)

Agent:
- System prompt + tool registry
- Executes SQL through Python tools
- Produces structured, readable responses

## 🗂️ Project Structure
/app  
  /agent  
    agent.py  
    tools.py  
    system_prompt.py  
  /static  
    index.html  
  /db  
    banking.db  
app.py  
README.md  

## 📥 Running the Project (GitHub Download)
1. Clone the repo  
   git clone https://github.com/<your-username>/<repo-name>.git  
   cd <repo-name>

2. Create a virtual environment  
   python3 -m venv venv  
   source venv/bin/activate (macOS/Linux)  
   venv\Scripts\activate (Windows)

3. Install dependencies  
   pip install -r requirements.txt  
   (If missing, create a requirements.txt containing: flask, mistralai)

4. Set your Mistral API key  
   export MISTRAL_API_KEY="your-key" (macOS/Linux)  
   set MISTRAL_API_KEY="your-key" (Windows)

5. Start the server  
   python main.py

6. Open the UI  
   http://localhost:5000

## 🧪 Example Flow
User: “Show monthly spend for customer 5”  
Agent: Runs SQL → returns rows → generates Markdown summary → UI renders formatted table + insights.

## 📈 Future Enhancements
- Inline charts  
- Multi‑customer comparisons  
- Export to CSV  
- Authentication  
- Additional analytics tools  

## 👤 Author
Built by Kiernan — aspiring AI Platform Engineer & full‑stack developer.
Designed for clarity, maintainability, and a smooth demo experience.
