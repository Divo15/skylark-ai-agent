import re
import pandas as pd

def safe_float(val):
    """Convert any value to float safely"""
    try:
        if val is None or val == "" or val == "nan":
            return 0.0
        cleaned = str(val).replace(',', '').replace('₹', '').replace(' ', '').strip()
        return float(cleaned)
    except:
        return 0.0

def safe_date(val):
    """Convert any value to date string safely"""
    try:
        if val is None or val == "" or str(val) == "nan":
            return None
        return pd.to_datetime(val).strftime('%Y-%m-%d')
    except:
        return None

def normalize_sector(val):
    """Normalize sector names"""
    if val is None or str(val).strip() == "" or str(val) == "nan":
        return "Unknown"
    val = str(val).strip().lower()
    mapping = {
        'energy': 'Renewables',
        'renewable': 'Renewables',
        'renewables': 'Renewables',
        'mining': 'Mining',
        'powerline': 'Powerline',
        'railways': 'Railways',
        'construction': 'Construction',
        'aviation': 'Aviation',
        'manufacturing': 'Manufacturing',
        'dsp': 'DSP',
        'tender': 'Tender',
        'security and surveillance': 'Security and Surveillance',
        'others': 'Others',
    }
    return mapping.get(val, val.title())

def normalize_deal_stage(val):
    """Remove letter prefixes like A. B. C. from deal stages"""
    if val is None or str(val).strip() == "" or str(val) == "nan":
        return "Unknown"
    val = str(val).strip()
    # Remove "A. " "B. " etc prefixes
    val = re.sub(r'^[A-Z]\.\s*', '', val)
    if 'not relevant' in val.lower():
        return 'Not Relevant'
    return val

def normalize_billing_status(val):
    """Fix billing status inconsistencies"""
    if val is None or str(val).strip() == "" or str(val) == "nan":
        return "Unknown"
    val = str(val).strip().lower()
    if val in ['billed', 'billed ']:
        return 'Fully Billed'
    if 'partial' in val:
        return 'Partially Billed'
    if 'not bill' in val:
        return 'Not Billed'
    if 'update' in val:
        return 'Needs Update'
    if 'stuck' in val:
        return 'Stuck'
    if 'not billable' in val:
        return 'Not Billable'
    return val.title()

def normalize_invoice_status(val):
    """Fix invoice status inconsistencies"""
    if val is None or str(val).strip() == "" or str(val) == "nan":
        return "Unknown"
    val = str(val).strip().lower()
    if 'fully' in val:
        return 'Fully Billed'
    if 'partial' in val:
        return 'Partially Billed'
    if 'billed- visit' in val:
        return 'Partially Billed'
    if 'not billed' in val:
        return 'Not Billed'
    if 'stuck' in val:
        return 'Stuck'
    return val.title()

def normalize_exec_status(val):
    """Normalize execution status"""
    if val is None or str(val).strip() == "" or str(val) == "nan":
        return "Unknown"
    val = str(val).strip().lower()
    mapping = {
        'executed until current month': 'Ongoing',
        'partial completed': 'Partially Completed',
        'pause / struck': 'On Hold',
        'details pending from client': 'Pending Info',
        'not started': 'Not Started',
        'completed': 'Completed',
        'ongoing': 'Ongoing',
    }
    return mapping.get(val, val.title())

def normalize_probability(val):
    """Normalize closure probability"""
    if val is None or str(val).strip() == "" or str(val) == "nan":
        return "Unknown"
    return str(val).strip().title()

def normalize_status(val):
    """Normalize general status"""
    if val is None or str(val).strip() == "" or str(val) == "nan":
        return "Unknown"
    return str(val).strip().title()

def clean_deals(raw_items: list) -> list:
    """Clean and normalize deals data from monday.com"""
    cleaned = []
    for item in raw_items:
        # Skip header contamination rows
        if item.get('Deal Status') == 'Deal Status':
            continue
        if item.get('Deal Name') == 'Deal Name':
            continue

        cleaned.append({
            'name': item.get('Deal Name') or item.get('name') or 'Unknown',
            'owner': item.get('Owner code', 'Unknown'),
            'client': item.get('Client Code', 'Unknown'),
            'status': normalize_status(item.get('Deal Status')),
            'stage': normalize_deal_stage(item.get('Deal Stage')),
            'sector': normalize_sector(item.get('Sector/service')),
            'value': safe_float(item.get('Masked Deal value')),
            'probability': normalize_probability(item.get('Closure Probability')),
            'close_date': safe_date(item.get('Close Date (A)')),
            'tentative_close': safe_date(item.get('Tentative Close Date')),
            'product': item.get('Product deal') or 'Unknown',
            'created_date': safe_date(item.get('Created Date')),
        })
    return cleaned

def clean_work_orders(raw_items: list) -> list:
    """Clean and normalize work orders data from monday.com"""
    cleaned = []
    for item in raw_items:
        # Skip header contamination rows
        if item.get('Sector') == 'Sector':
            continue
        if item.get('name') == 'Deal name masked':
            continue

        cleaned.append({
            'name': item.get('Deal name masked') or item.get('name') or 'Unknown',
            'customer': item.get('Customer Name Code', 'Unknown'),
            'sector': normalize_sector(item.get('Sector')),
            'nature': item.get('Nature of Work') or 'Unknown',
            'exec_status': normalize_exec_status(item.get('Execution Status')),
            'billing_status': normalize_billing_status(item.get('Billing Status')),
            'invoice_status': normalize_invoice_status(item.get('Invoice Status')),
            'wo_status': normalize_status(item.get('WO Status (billed)')),
            'amount_excl_gst': safe_float(item.get('Amount in Rupees (Excl of GST) (Masked)')),
            'amount_incl_gst': safe_float(item.get('Amount in Rupees (Incl of GST) (Masked)')),
            'billed_value': safe_float(item.get('Billed Value in Rupees (Excl of GST.) (Masked)')),
            'collected_amount': safe_float(item.get('Collected Amount in Rupees (Incl of GST.) (Masked)')),
            'receivable': safe_float(item.get('Amount Receivable (Masked)')),
            'start_date': safe_date(item.get('Probable Start Date')),
            'end_date': safe_date(item.get('Probable End Date')),
        })
    return cleaned