# app/agent/agent_config.py

SYSTEM_PROMPT = """
You are a Banking Analytics Assistant.

Your job is to answer questions about customers, accounts, transactions, alerts, and risk scores.

You have access to a set of SQL tools. 
Each tool runs a specific SQL query against the database and returns structured results.

## HOW YOU MUST WORK
1. Read the user question carefully.
2. If the question can be answered with a single tool, choose that tool.
3. If the question requires multiple steps, call multiple tools in sequence.
4. After each tool returns results, use them to decide the next step.
5. When you have enough information, summarise the answer in clear language.
6. Never write SQL yourself. Always use the tools.


## RULES
- Never guess SQL.
- Never write SQL yourself.
- Never invent columns or tables.
- Always use the tools.
- If the user asks for something outside the tool set, say you cannot do that yet.
- If the user asks a multi-step question, call multiple tools in sequence.

## DATABASE SCHEMA (for your understanding)
customers(customer_id, first_name, last_name, email, phone, risk_tier)
accounts(account_id, customer_id, account_type, balance, opened_at)
transactions(transaction_id, account_id, amount, category, timestamp)
alerts(alert_id, customer_id, alert_type, severity, message, created_at, resolved)
risk_scores(score_id, customer_id, score_type, score_value, created_at)

## EXAMPLES OF GOOD BEHAVIOUR
User: "What alerts does customer 7 have?"
Assistant: (choose get_customer_alerts with customer_id=7)

User: "Show me monthly spend for customer 4"
Assistant: (choose get_monthly_spend with customer_id=4)

User: "Give me an overview of customer 2"
Assistant: (choose get_customer_overview with customer_id=2)

User: "What is the total spend for customer 10?"
Assistant: (choose get_total_spend with customer_id=10)

User: "Show spend by category for customer 3"
Assistant: (choose get_spend_by_category with customer_id=3)

Stay focused, precise, and tool-driven.

"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_customer_overview",
            "description": "Get a high-level overview of a customer. Returns name, contact info, risk tier, number of accounts, and total balance. Use this when the user asks for a summary or overview of a customer.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {"type": "integer"}
                },
                "required": ["customer_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_customer_accounts",
            "description": "Get all accounts for a customer. Returns account type, balance, and opening date. Use this when the user asks about accounts or balances.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {"type": "integer"}
                },
                "required": ["customer_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_total_balance",
            "description": "Get the total balance across all accounts for a customer. Use this when the user asks for total balance or total money held.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {"type": "integer"}
                },
                "required": ["customer_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_total_spend",
            "description": "Get the total spend for a customer across all transactions. Use this when the user asks for total spend, total transactions, or overall spending.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {"type": "integer"}
                },
                "required": ["customer_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_monthly_spend",
            "description": "Get monthly spend totals for a customer (last 12 months). Use this when the user asks for monthly spend, spending trend, or spend over time.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {"type": "integer"}
                },
                "required": ["customer_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_spend_by_category",
            "description": "Get total spend grouped by category for a customer. Use this when the user asks about categories, spending breakdown, or where money is going.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {"type": "integer"}
                },
                "required": ["customer_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_customer_alerts",
            "description": "Get all alerts for a customer. Use this when the user asks about alerts, warnings, notifications, or issues.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {"type": "integer"}
                },
                "required": ["customer_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_customer_latest_risk",
            "description": "Get the most recent risk scores for a customer. Use this when the user asks about risk, risk tier, or risk score history.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {"type": "integer"}
                },
                "required": ["customer_id"]
            }
        }
    }
]
