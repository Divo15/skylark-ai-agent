TOOLS = [
    {
        "name": "get_deals_data",
        "description": """Fetch live deals and pipeline data from monday.com.
        Use this for questions about:
        - Pipeline health and deal stages
        - Revenue forecasts and deal values
        - Sector wise deal performance
        - Deal status (Open, Won, Dead, On Hold)
        - Closure probability (High, Medium, Low)
        - Specific owner or client deals""",
        "input_schema": {
            "type": "object",
            "properties": {
                "sector": {
                    "type": "string",
                    "description": "Filter by sector. Options: Mining, Powerline, Renewables, Railways, Construction, Aviation, Manufacturing, DSP, Tender, Others"
                },
                "status": {
                    "type": "string",
                    "description": "Filter by deal status. Options: Open, Won, Dead, On Hold"
                },
                "stage": {
                    "type": "string",
                    "description": "Filter by deal stage e.g. Sales Qualified Leads, Proposal Sent, Negotiations, Project Won"
                }
            },
            "required": []
        }
    },
    {
        "name": "get_work_orders_data",
        "description": """Fetch live work orders and operations data from monday.com.
        Use this for questions about:
        - Active and completed projects
        - Billing and invoice status
        - Amounts billed and collected
        - Amounts receivable and pending
        - Execution status of work orders
        - Sector wise operational performance""",
        "input_schema": {
            "type": "object",
            "properties": {
                "sector": {
                    "type": "string",
                    "description": "Filter by sector. Options: Mining, Powerline, Renewables, Railways, Construction, Others"
                },
                "status": {
                    "type": "string",
                    "description": "Filter by execution or billing status"
                }
            },
            "required": []
        }
    },
    {
        "name": "get_combined_data",
        "description": """Fetch BOTH deals AND work orders data together from monday.com.
        Use this for questions about:
        - Overall business health
        - Full sector analysis across pipeline and operations
        - Comparing pipeline vs active work
        - Total revenue across all sources
        - Company wide performance summary""",
        "input_schema": {
            "type": "object",
            "properties": {
                "sector": {
                    "type": "string",
                    "description": "Filter both boards by sector"
                }
            },
            "required": []
        }
    }
]