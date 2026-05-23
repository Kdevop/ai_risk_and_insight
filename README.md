# AI Risk & Insight Platform (Under Development)

This repository contains the early-stage development of an AI-driven Risk & Insight platform.  
The system is being built using:

- **Flask** for the backend API  
- **Google Cloud Run** for serverless deployment  
- **Google Cloud SQL (PostgreSQL)** for data storage  
- **Cloud SQL Python Connector** for secure database access  
- **Python-based analytics** for risk scoring, explainability, and insights  

## Current Status

🚧 **This project is actively under development.**  
Core infrastructure is being assembled, including:

- Flask application structure  
- Cloud SQL connectivity  
- Local development environment  
- Initial test routes and diagnostics  

Major features such as the agentic workflow, analytics engine, and UI will be added in upcoming stages.

## Local Development

To run the app locally:

1. Create a `.env` file with your database settings  
2. Install dependencies  
3. Start the Flask server  
4. Test the database connection via `/db-test`

## Deployment

Deployment will be handled through **GitHub → Cloud Run continuous deployment**, with Cloud SQL attached for secure database access.

---

More documentation will be added as the project evolves.
