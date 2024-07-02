#!/usr/bin/env 
import re
import sys
from typing import List, Dict
import PyPDF2
import pandas as pd

def extract_text_from_pdf(pdf_path: str) -> str:
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text

def extract_transactions(statement_text: str) -> List[Dict[str, str]]:
    # Find the transaction section
    transaction_section = re.search(r'Transaction Detail(.*?)Total Fees Charged This Period', statement_text, re.DOTALL)
    
    if not transaction_section:
        print("Transaction section not found")
        return []

    transaction_text = transaction_section.group(1)
    
    # Regular expression to match transactions
    transaction_pattern = re.compile(r'(\d{2}/\d{2})\s+(\S+)\s+(.*?)\s+([-$\d,.]+)$', re.MULTILINE)
    
    transactions = []
    
    for match in transaction_pattern.finditer(transaction_text):
        date, reference, description, amount = match.groups()
        
        # Clean up the amount
        amount = amount.replace('$', '').replace(',', '')
        
        transactions.append({
            'date': date,
            'reference': reference,
            'description': description.strip(),
            'amount': float(amount)
        })
    
    return transactions

def parse_credit_card_statement(statement_text: str) -> Dict[str, any]:
    result = {
        'account_number': '',
        'statement_date': '',
        'payment_due_date': '',
        'new_balance': '',
        'minimum_payment_due': '',
        'transactions': []
    }
    
    # Extract account number
    account_match = re.search(r'Account Number ending in (\d+)', statement_text)
    if account_match:
        result['account_number'] = account_match.group(1)
    
    # Extract statement date
    date_match = re.search(r'(\d{2}/\d{2}/\d{4}) to (\d{2}/\d{2}/\d{4})', statement_text)
    if date_match:
        result['statement_date'] = date_match.group(2)
    
    # Extract payment due date
    due_date_match = re.search(r'Payment Due Date: (\d{2}/\d{2}/\d{4})', statement_text)
    if due_date_match:
        result['payment_due_date'] = due_date_match.group(1)
    
    # Extract new balance
    balance_match = re.search(r'New Balance: \$([\d,]+\.\d{2})', statement_text)
    if balance_match:
        result['new_balance'] = float(balance_match.group(1).replace(',', ''))
    
    # Extract minimum payment due
    min_payment_match = re.search(r'Total Minimum Payment Due: \$([\d,]+\.\d{2})', statement_text)
    if min_payment_match:
        result['minimum_payment_due'] = float(min_payment_match.group(1).replace(',', ''))
    
    # Extract transactions
    result['transactions'] = extract_transactions(statement_text)
    
    return result

def parse_credit_card_statement_from_pdf(pdf_path: str) -> Dict[str, any]:
    # Extract text from PDF
    statement_text = extract_text_from_pdf(pdf_path)
    
    # Debugging: Print the first 500 characters of the extracted text
    print("First 500 characters of extracted text:")
    print(statement_text[:500])
    
    # Parse the extracted text
    return parse_credit_card_statement(statement_text)


# def credit_card_statement_to_csv(parsed_data: Dict[str, any], output_file: str) -> None:
#     # Create a DataFrame for the overall statement information
#     statement_info = pd.DataFrame({
#         'Account Number': [parsed_data['account_number']],
#         'Statement Date': [parsed_data['statement_date']],
#         'Payment Due Date': [parsed_data['payment_due_date']],
#         'New Balance': [parsed_data['new_balance']],
#         'Minimum Payment Due': [parsed_data['minimum_payment_due']]
#     })

#     # Create a DataFrame for the transactions
#     transactions_df = pd.DataFrame(parsed_data['transactions'])

#     # Combine the two DataFrames
#     statement_info.to_csv(output_file, index=False)
#     transactions_df.to_csv(output_file, index=False)

#     print(f"Credit card statement data has been saved to {output_file}")
    
def credit_card_transactions_to_csv(transactions: List[Dict[str, any]], output_file: str) -> None:
    # Create a DataFrame for the transactions
    transactions_df = pd.DataFrame(transactions)

    # Ensure the columns are in a specific order
    column_order = ['date', 'reference', 'description', 'amount']
    transactions_df = transactions_df.reindex(columns=column_order)

    # Sort transactions by date
    transactions_df['date'] = pd.to_datetime(transactions_df['date'], format='%m/%d')
    transactions_df = transactions_df.sort_values('date')

    # Format the date column back to string (MM/DD format)
    transactions_df['date'] = transactions_df['date'].dt.strftime('%m/%d')

    # Save the DataFrame to a CSV file
    transactions_df.to_csv(output_file, index=False)

    print(f"Credit card transactions have been saved to {output_file}")

if __name__ == "__main__":
    for pdf_path in sys.argv[1:]:  # Skip the first argument, which is the script name
        parsed_data = parse_credit_card_statement_from_pdf(pdf_path)
        csv_output_path = pdf_path.rsplit('.', 1)[0] + '.csv'  # Replace .pdf with .csv
        credit_card_transactions_to_csv(parsed_data['transactions'], csv_output_path)



# Example usage
# pdf_path = "/Users/wylerzahm/Desktop/fin2/amzn/1.feb.pdf"
# parsed_data = parse_credit_card_statement_from_pdf(pdf_path)
# print("\nParsed data:")
# print(parsed_data)

# parse.credit_card_statement_to_csv(parsed_data, "output.csv")
# parse.credit_card_transactions_to_csv(parsed_data['transactions'], "transactions.csv")