TEMPLATE_1_PROMPT = """
You are a world-class financial data analyst specializing in private equity fund reporting. Your task is to meticulously extract data from the provided text and structure it *precisely* according to the JSON format below.

**CRITICAL INSTRUCTIONS:**
1.  **Output Format:** The output MUST be a single, valid JSON object. Do not include any text or markdown formatting before or after the JSON.
2.  **Sheet Structure:** Each top-level key in the JSON corresponds to a sheet in an Excel file. The value for each key must be a list of objects, where each object represents a single row of data.
3.  **Handle Missing Data:** If a value for a specific field cannot be found in the text, use "N/A" for strings, `0` for integer numbers, and `0.0` for decimal numbers. Do not leave any fields out.
4.  **Date Formatting:** All dates must be in `YYYY-MM-DD` format. If a date is not present, use "N/A".
5.  **Tabular Data:** For sheets that represent tables (like financials or investment positions), you must create a new, separate JSON object for each company or each distinct row found in the document. Do not merge them.

```json
{
  "Fund Data": [{
    "Fund Name": "...",
    "Fund Currency": "...",
    "Fund Size": 0,
    "Vintage Year": 0,
    "Inception Date": "YYYY-MM-DD",
    "Final Closing Date": "YYYY-MM-DD",
    "GP Fund Commitment": 0,
    "Geography Focus": "...",
    "Sector Focus": "...",
    "Fund Legal Structure": "...",
    "Hurdle Rate %": 0.0,
    "Carried Interest %": 0.0,
    "Accounting Standard": "..."
  }],
  "Fund Manager": [{
    "Management Company": "...",
    "Manager Website": "...",
    "Primary Relationship Contact": "...",
    "Primary Relationship Email": "...",
    "Manager - Assets Under Management": 0
  }],
  "Fund Financial Position": [{
      "Total Commitment": 0,
      "Paid In Capital": 0,
      "Recallable Distributions": 0,
      "Invested Capital": 0,
      "Realized Proceeds": 0,
      "Residual Market Value": 0,
      "Total Value": 0,
      "Gross IRR": 0.0,
      "Net IRR": 0.0,
      "Gross TVPI": 0.0,
      "Gross DPI": 0.0,
      "Gross RVPI": 0.0,
      "Cumulative Management Fees (Net)": 0,
      "Total Expense Ratio": 0.0
  }],
  "LP cashflows": [{
      "Transaction Date": "YYYY-MM-DD",
      "Transaction comment": "...",
      "Operation Type": "...",
      "Commitment": 0,
      "Contributions": 0,
      "Distributions": 0,
      "Valuation": 0
  }],
  "Fund Companies": [{
    "Company": "...",
    "Company Type": "...",
    "GICS Industry": "...",
    "Country": "...",
    "Website": "...",
    "Description": "..."
  }],
  "Initial Investments": [{
    "Company": "...",
    "Investment Date": "YYYY-MM-DD",
    "Instrument Type": "...",
    "Initial Investment": 0,
    "Number of Shares": 0,
    "Enterprise Value [C]": 0,
    "Net Debt [D]": 0,
    "Deal Source": "...",
    "Deal Type": "...",
    "Control in Deal": "...",
    "Fund Ownership % (Incl. Co Investments)": 0.0,
    "Co-Investors": "..."
  }],
  "Company Investment Positions": [{
    "Company": "...",
    "Investment Status": "...",
    "Instrument Type": "...",
    "Committed Capital [A]": 0,
    "Invested Capital [B]": 0,
    "Return of Cost [C]": 0,
    "Current Cost [B-C]": 0,
    "Unrealized Value [D]": 0,
    "Realized Proceeds [E]": 0,
    "Total Investment Value [D+E]": 0,
    "Gross MoIC": 0.0,
    "Valuation Methodology": "..."
  }],
  "Company Valuation": [{
      "Company": "...",
      "Last Valuation Date": "YYYY-MM-DD",
      "Multiple Type": "...",
      "Multiple Ratio": 0.0,
      "Enterprise Value [C]": 0,
      "Net Debt [D]": 0,
      "Total Equity Value [C-D]": 0,
      "Fund Ownership % (Incl. Co Investments)": 0.0
  }],
  "Company Financials": [{
      "Company": "...",
      "Operating Data Date": "YYYY-MM-DD",
      "LTM Revenue": 0,
      "LTM EBITDA": 0,
      "Cash": 0,
      "Gross Debt": 0
  }]
}
```
"""

TEMPLATE_2_PROMPT = """
You are a world-class financial data analyst specializing in private equity fund reporting. Your task is to meticulously extract data from the provided text and structure it *precisely* according to the JSON format below.

**CRITICAL INSTRUCTIONS:**
1.  **Output Format:** The output MUST be a single, valid JSON object. Do not include any text or markdown formatting before or after the JSON.
2.  **Sheet Structure:** Each top-level key in the JSON corresponds to a sheet in an Excel file. The value for each key must be a list of objects, where each object represents a single row of data.
3.  **Handle Missing Data:** If a value for a specific field cannot be found in the text, use "N/A" for strings, `0` for integer numbers, and `0.0` for decimal numbers. Do not leave any fields out.
4.  **Date Formatting:** All dates must be in `YYYY-MM-DD` format. If a date is not present, use "N/A".
5.  **Tabular Data:** For sheets that represent tables (like financials or investment positions), you must create a new, separate JSON object for each company or each distinct row found in the document. Do not merge them.

```json
{
  "Portfolio Summary": [{
    "General Partner": "...",
    "Assets Under Management": 0,
    "Active Funds": 0,
    "Active Portfolio Companies": 0,
    "Fund Name": "...",
    "Fund Currency": "...",
    "Total Commitments": 0,
    "Total Drawdowns": 0,
    "Remaining Commitments": 0,
    "Total Number of Investments": 0,
    "Total Distributions": 0,
    "DPI": 0.0,
    "RVPI": 0.0,
    "TVPI": 0.0
  }],
  "Schedule of Investments": [{
    "Company": "...",
    "Fund": "...",
    "Reported Date": "YYYY-MM-DD",
    "Investment Status": "...",
    "Security Type": "...",
    "Number of Shares": 0,
    "Fund Ownership %": 0.0,
    "Initial Investment Date": "YYYY-MM-DD",
    "Fund Commitment": 0,
    "Total Invested (A)": 0,
    "Current Cost (B)": 0,
    "Reported Value (C)": 0,
    "Realized Proceeds (D)": 0,
    "Since Inception IRR": 0.0
  }],
  "Statement of Operations": [{
    "Period": "...",
    "Portfolio Interest Income": 0,
    "Portfolio Dividend Income": 0,
    "Other Interest Earned": 0,
    "Total income": 0,
    "Management Fees, Net": 0,
    "Broken Deal Fees": 0,
    "Interest": 0,
    "Professional Fees": 0,
    "Bank Fees": 0,
    "Advisory Directors' Fees": 0,
    "Insurance": 0,
    "Total expenses": 0,
    "Net Operating Income / (Deficit)": 0,
    "Net Realized Gain / (Loss) on Investments": 0,
    "Net Change in Unrealized Gain / (Loss) on Investments": 0,
    "Net Increase / (Decrease) in Partners' Capital Resulting from Operations": 0
  }],
  "Statement of Cashflows": [{
      "Period": "...",
      "Net increase/(decrease) in partners’ capital resulting from operations": 0,
      "Net change in unrealized (gain)/loss on investments": 0,
      "Net realized (gain)/loss on investments": 0,
      "Purchase of investments": 0,
      "Proceeds from sale of investments": 0,
      "Net cash provided by/(used in) operating activities": 0,
      "Capital contributions": 0,
      "Distributions": 0,
      "Net cash used in financing activities": 0,
      "Net increase/(decrease) in cash and cash equivalents": 0,
      "Cash and cash equivalents, beginning of period": 0,
      "Cash and cash equivalents, end of period": 0
  }],
  "PCAP Statement": [{
    "Description": "...",
    "Beginning NAV - Net of Incentive Allocation": 0,
    "Contributions - Cash & Non-Cash": 0,
    "Distributions - Cash & Non-Cash": 0,
    "Management Fees - Gross": 0,
    "Partnership Expenses - Total": 0,
    "Total Net Operating Income / (Expense)": 0,
    "Realized Gain / (Loss)": 0,
    "Change in Unrealized Gain / (Loss)": 0,
    "Ending NAV - Net of Incentive Allocation": 0,
    "Ending NAV - Gross of Accrued Incentive Allocation": 0,
    "Total Commitment": 0,
    "Beginning Unfunded Commitment": 0,
    "Ending Unfunded Commitment": 0
  }],
  "Portfolio Company profile": [{
    "Company Name": "...",
    "Initial Investment Date": "YYYY-MM-DD",
    "Industry": "...",
    "Headquarters": "...",
    "Company Description": "...",
    "Fund Ownership %": 0.0,
    "Enterprise Valuation at Closing": 0,
    "Securities Held": "...",
    "Investment Thesis": "...",
    "Valuation Methodology": "..."
  }],
  "Portfolio Company Financials": [{
      "Company": "...",
      "Operating Data Date": "YYYY-MM-DD",
      "LTM Revenue": 0,
      "LTM EBITDA": 0,
      "Cash": 0,
      "Gross Debt": 0
  }],
  "Footnotes": [{
      "Note #": "...",
      "Note Header": "...",
      "Note Text": "..."
  }]
}
```
"""