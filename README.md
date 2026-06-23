# Banking Analytics Assistant
A AI‑powered financial analytics assistant that turns natural‑language questions into SQL, statistical analysis, anomaly detection, and visual insights. It is designed for business users who understand their data and context — but may not have SQL or Python skills.

Across organisations, analysts often rely on technical teams to access data through a “front door” process. Athena removes this bottleneck by democratising access to analytics. Users can explore data, run analysis, and generate insights without writing a single line of code.

## Key Features
### Natural language to SQL
Ask questions in plain english - the tool generates and executes the SQL automatically.
### Automated statistical analysis
Summary statistics, percentiles, distributions, and descriptive metrics.
### Anomaly detection
Z-score based detection of unusual transations or outliers.
### Visual analysis
Monthly trents, cagetory breakdowns, (under development: scatter plots, regression lines and more)
### Customer insights
Tools for retrieving customer lists and individual customer overviews.
### DataFrame registry
Each SQL query registers a DataFrame, enabling multi-step reasoning and follow-up questions. 
### Clean, intuitive UI
Right-panel toggles for SQL, preview, and detailed analysis. Left-panel holds the user-agent chat.
### Agentic workflow
Mistral LLM orchestrates tools, executes SQL, runs analysis, and summarises insights

## Tools
### run_sql_query
Executes SQL against the database and registers the resulting DataFrame.
### generate_statistical_analysis
Computes summary statistics, percentiles and descriptiive metrics.
### generate_visual_analysis
Generates visual insights such as monthly trends, category breakdown, and scatter plots
### get customer_overview
Returns a profile of a specific customer, including spend patters and recent activity.

## Tech Stack
- **Python / FastAPI backend** - core agentic logic, tool ochestration, SQL execution, analytics pipeline
- **Flask** - lightweight web layer that serves the UI and forwards user queries to FastAPI 
- **Mistral LLM Agent loop** - natural-language understanding, SQL generation, and reasoning 
- **SQL database** - transactional and analytical data source
- **Custom analytics tools** - statistical analysis, anomaly detection, visual insights
- **HTML/CSS/Javascript frontend** - chat interface, SQL viewer, preview table analysis panel

## Project Structure
```text
app/
├── agent/
│   ├── agent.py
│   ├── agent_config.py
│   └── tools/
│       └── agent_tools.py
├── fastapi_app/
│   └── main.py
├── routes/
│   ├── app.py
│   ├── clear_chat.py
│   ├── db_tests.py
│   └── home.py
├── services/
│   ├── analytics.py
│   ├── explainability.py
│   └── risk_model.py
├── templates/
│   └── index.html
├── static/
│   ├── charts/
│   ├── css/
│   │   └── styles.css
│   └── js/
│       └── app.py
├── db/
│   ├── connection.py
│   └── queries.py
└── tests/
    ├── sql_test.py
    ├── test_agent.py
    ├── test_chat.py
    ├── test_stats.py
    ├── test_visuals.py
    └── test_tools.py

logs/
DockerFiles/
README.md
requirements.txt
```

## Running the Project (GitHub Download)
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

5. Start the server and flask
   uvicorn app.fastapi_app.main:app
   python -m flask --app app.main run

6. Open the UI  
   http://localhost:5000

## Example Queries
- "Show me monthly sepnd for customer 4"
- "Find anomalies in the last 30 days"
- "Give me summart statistics for the last 12 months of transactions"
- "Compare groceries vs shapping for customer 3"
- "Plot entertainment spend over the last 12 months"

## Future Enhancements
- Additional visualisations 
- Risk scoring and fraud-pattern detection
- Customer segmentation  
- Export to CSV  
- Additional analytics tools  
- Natural language chart editing
- UI improvements

## Author
Built by Kiernan — aspiring AI Business Analyst with background in project management and change.
Designed for clarity, maintainability, and a smooth demo experience.

## License
MIT License

## Supporting Docs
See agentic_ai_insights_platform_brd.pdf for further details on the project