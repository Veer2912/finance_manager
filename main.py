import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import json
import os
import io

# File path for data persistence
DATA_FILE = 'finance_data.json'

# Initialize session state for income, expenses, and currency
if 'income_data' not in st.session_state:
    st.session_state.income_data = []

if 'expense_data' not in st.session_state:
    st.session_state.expense_data = []

if 'currency' not in st.session_state:
    st.session_state.currency = "USD"

# Load data from JSON file
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as file:
            data = json.load(file)
            st.session_state.income_data = data.get('income_data', [])
            st.session_state.expense_data = data.get('expense_data', [])
            st.session_state.currency = data.get('currency', "USD")

# Save data to JSON file
def save_data():
    data = {
        'income_data': st.session_state.income_data,
        'expense_data': st.session_state.expense_data,
        'currency': st.session_state.currency
    }
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file, default=str, indent=4)

# Functions to add income, expense, and calculate savings
def add_income(source, amount):
    st.session_state.income_data.append({
        "source": source,
        "amount": float(amount),
        "date": datetime.datetime.now().isoformat(),
        "currency": st.session_state.currency
    })
    save_data()

def add_expense(category, amount):
    st.session_state.expense_data.append({
        "category": category,
        "amount": float(amount),
        "date": datetime.datetime.now().isoformat(),
        "currency": st.session_state.currency
    })
    save_data()

def calculate_savings(income_data, expense_data):
    total_income = sum(item['amount'] for item in income_data)
    total_expenses = sum(item['amount'] for item in expense_data)
    return total_income - total_expenses

def filter_data_by_month(data, month, year):
    return [item for item in data if datetime.datetime.fromisoformat(item['date']).month == month and datetime.datetime.fromisoformat(item['date']).year == year]

def filter_data_by_year(data, year):
    return [item for item in data if datetime.datetime.fromisoformat(item['date']).year == year]

def generate_csv_report(income_data, expense_data, savings, month, year):
    month_name = datetime.date(1900, month, 1).strftime('%B')
    
    # Create dataframes
    df_income = pd.DataFrame(income_data)
    df_expense = pd.DataFrame(expense_data)
    
    # Generate CSV output
    output = io.StringIO()
    output.write(f"Report for {month_name} {year}\n")
    output.write("\nIncome:\n")
    df_income.to_csv(output, index=False)
    
    output.write("\nExpenses:\n")
    df_expense.to_csv(output, index=False)
    
    output.write(f"\nTotal Savings: {savings:.2f} {st.session_state.currency}\n")
    
    return output.getvalue()

# Load data when the app starts
load_data()

# Streamlit app layout
st.title("Personal Finance Manager")

# Currency selection
currency_options = ["USD", "EUR", "GBP", "INR"]
st.session_state.currency = st.selectbox("Select your currency:", currency_options)

st.sidebar.header("Input Data")

# Income Section
st.sidebar.subheader("Add Income")
income_source = st.sidebar.text_input("Income Source")
income_amount = st.sidebar.number_input(f"Amount ({st.session_state.currency})", min_value=0.0, format="%.2f", key="income_amount")
if st.sidebar.button("Add Income", key="add_income"):
    if income_source and income_amount > 0:
        add_income(income_source, income_amount)
        st.sidebar.success(f"Income of {income_amount} {st.session_state.currency} from {income_source} added.")
    else:
        st.sidebar.error("Please provide both source and amount.")

# Expense Section
st.sidebar.subheader("Add Expense")
expense_category = st.sidebar.text_input("Expense Category")
expense_amount = st.sidebar.number_input(f"Amount ({st.session_state.currency})", min_value=0.0, format="%.2f", key="expense_amount")
if st.sidebar.button("Add Expense", key="add_expense"):
    if expense_category and expense_amount > 0:
        add_expense(expense_category, expense_amount)
        st.sidebar.success(f"Expense of {expense_amount} {st.session_state.currency} on {expense_category} added.")
    else:
        st.sidebar.error("Please provide both category and amount.")

# Display Current Month Data
current_month = datetime.datetime.now().month
current_year = datetime.datetime.now().year

filtered_income_data = filter_data_by_month(st.session_state.income_data, current_month, current_year)
filtered_expense_data = filter_data_by_month(st.session_state.expense_data, current_month, current_year)
current_savings = calculate_savings(filtered_income_data, filtered_expense_data)

st.header("Current Month Financial Summary")

if filtered_income_data or filtered_expense_data:
    st.subheader(f"Total Savings for {datetime.date(1900, current_month, 1).strftime('%B')} {current_year}: {current_savings:.2f} {st.session_state.currency}")

    st.subheader("Income Report")
    if filtered_income_data:
        st.write(pd.DataFrame(filtered_income_data))
    else:
        st.write("No income data available for the current month.")

    st.subheader("Expense Report")
    if filtered_expense_data:
        st.write(pd.DataFrame(filtered_expense_data))
    else:
        st.write("No expense data available for the current month.")

    st.subheader("Visualizations")
    
    # Visualize Expenses for the current month
    if st.button("Visualize Current Month Expenses"):
        if filtered_expense_data:
            df_expense = pd.DataFrame(filtered_expense_data)
            fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
            df_expense.groupby('category')['amount'].sum().plot(kind='pie', autopct='%1.1f%%', ax=ax)
            ax.set_ylabel('')
            ax.set_title(f'Expense Distribution - {datetime.date(1900, current_month, 1).strftime("%B")} {current_year}')
            st.pyplot(fig)
        else:
            st.error("No expense data to visualize for the current month.")
    
    # Visualize Savings for the current year
    if st.button("Visualize Savings for the Year"):
        income_data_year = filter_data_by_year(st.session_state.income_data, current_year)
        expense_data_year = filter_data_by_year(st.session_state.expense_data, current_year)

        if income_data_year or expense_data_year:
            monthly_savings = []
            months = range(1, 13)
            for month in months:
                monthly_income = filter_data_by_month(income_data_year, month, current_year)
                monthly_expense = filter_data_by_month(expense_data_year, month, current_year)
                savings = calculate_savings(monthly_income, monthly_expense)
                monthly_savings.append(savings)

            fig, ax = plt.subplots(figsize=(12, 6), dpi=100)  # Set figure size and DPI
            ax.bar(months, monthly_savings, tick_label=[datetime.date(1900, m, 1).strftime('%B') for m in months])
            ax.set_title(f'Savings by Month - {current_year}')
            ax.set_xlabel('Month')
            ax.set_ylabel(f'Savings ({st.session_state.currency})')
            plt.xticks(rotation=45)  # Rotate month labels for better readability
            st.pyplot(fig)
        else:
            st.error("No data to visualize for the current year.")

# Month and Year Selection for Specific Reports
st.header("View Data for a Specific Month and Year")

selected_month = st.selectbox("Select Month:", range(1, 13), format_func=lambda x: datetime.date(1900, x, 1).strftime('%B'))
selected_year = st.selectbox("Select Year:", range(datetime.datetime.now().year - 5, datetime.datetime.now().year + 1))

# Filter data by selected month and year
filtered_income_data = filter_data_by_month(st.session_state.income_data, selected_month, selected_year)
filtered_expense_data = filter_data_by_month(st.session_state.expense_data, selected_month, selected_year)

if filtered_income_data or filtered_expense_data:
    savings = calculate_savings(filtered_income_data, filtered_expense_data)
    st.subheader(f"Total Savings for {datetime.date(1900, selected_month, 1).strftime('%B')} {selected_year}: {savings:.2f} {st.session_state.currency}")

    if st.checkbox("Show Detailed Report"):
        st.subheader("Income Report")
        if filtered_income_data:
            st.write(pd.DataFrame(filtered_income_data))
        else:
            st.write("No income data available for this period.")

        st.subheader("Expense Report")
        if filtered_expense_data:
            st.write(pd.DataFrame(filtered_expense_data))
        else:
            st.write("No expense data available for this period.")

    st.subheader("Visualizations")
    
    # Visualize Expenses for the selected month
    if st.button("Visualize Expenses"):
        if filtered_expense_data:
            df_expense = pd.DataFrame(filtered_expense_data)
            fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
            df_expense.groupby('category')['amount'].sum().plot(kind='pie', autopct='%1.1f%%', ax=ax)
            ax.set_ylabel('')
            ax.set_title(f'Expense Distribution - {datetime.date(1900, selected_month, 1).strftime("%B")} {selected_year}')
            st.pyplot(fig)
        else:
            st.error("No expense data to visualize for this period.")
    
    # Generate CSV report
    csv_report = generate_csv_report(filtered_income_data, filtered_expense_data, savings, selected_month, selected_year)
    st.download_button(
        label="Download Report as CSV",
        data=csv_report,
        file_name=f"{datetime.date(1900, selected_month, 1).strftime('%B')}_{selected_year}_report.csv",
        mime="text/csv"
    )
else:
    st.write("No data available for the selected month and year. Please add income and expenses using the sidebar.")
