import gradio as gr
import pandas as pd
from accounts import Account, get_share_price

# Global variable to store the account
account = None

def create_account(user_id, initial_deposit):
    """Create a new account with the given user ID and initial deposit."""
    global account
    try:
        initial_deposit = float(initial_deposit)
        account = Account(user_id, initial_deposit)
        return f"Account created for {user_id} with initial deposit of ${initial_deposit:.2f}"
    except ValueError as e:
        return f"Error: {str(e)}"

def deposit_funds(amount):
    """Deposit funds into the account."""
    global account
    if account is None:
        return "Please create an account first."
    
    try:
        amount = float(amount)
        if account.deposit(amount):
            return f"Successfully deposited ${amount:.2f}. New balance: ${account.balance:.2f}"
        else:
            return "Deposit failed. Amount must be positive."
    except ValueError:
        return "Invalid amount. Please enter a valid number."

def withdraw_funds(amount):
    """Withdraw funds from the account."""
    global account
    if account is None:
        return "Please create an account first."
    
    try:
        amount = float(amount)
        if account.withdraw(amount):
            return f"Successfully withdrew ${amount:.2f}. New balance: ${account.balance:.2f}"
        else:
            return "Withdrawal failed. Amount must be positive and not exceed your balance."
    except ValueError:
        return "Invalid amount. Please enter a valid number."

def buy_shares(symbol, quantity):
    """Buy shares of the specified stock."""
    global account
    if account is None:
        return "Please create an account first."
    
    try:
        quantity = int(quantity)
        symbol = symbol.upper()
        price = get_share_price(symbol)
        
        if price == 0.0:
            return f"Invalid stock symbol: {symbol}"
        
        if account.buy_shares(symbol, quantity):
            return f"Successfully bought {quantity} shares of {symbol} at ${price:.2f} each. Total cost: ${price * quantity:.2f}"
        else:
            return f"Failed to buy shares. Check that you have enough funds (${account.balance:.2f} available) and entered a valid quantity."
    except ValueError:
        return "Invalid quantity. Please enter a valid number."

def sell_shares(symbol, quantity):
    """Sell shares of the specified stock."""
    global account
    if account is None:
        return "Please create an account first."
    
    try:
        quantity = int(quantity)
        symbol = symbol.upper()
        price = get_share_price(symbol)
        
        if price == 0.0:
            return f"Invalid stock symbol: {symbol}"
        
        if account.sell_shares(symbol, quantity):
            return f"Successfully sold {quantity} shares of {symbol} at ${price:.2f} each. Total value: ${price * quantity:.2f}"
        else:
            holdings = account.get_holdings()
            if symbol in holdings:
                return f"Failed to sell shares. You only have {holdings[symbol]} shares of {symbol}."
            else:
                return f"Failed to sell shares. You don't own any shares of {symbol}."
    except ValueError:
        return "Invalid quantity. Please enter a valid number."

def get_portfolio_summary():
    """Get a summary of the user's portfolio."""
    global account
    if account is None:
        return "Please create an account first."
    
    holdings = account.get_holdings()
    if not holdings:
        return f"You don't have any shares. Cash balance: ${account.balance:.2f}"
    
    total_value = account.get_portfolio_value()
    profit_loss = account.get_profit_or_loss()
    
    summary = f"Portfolio Summary for {account.user_id}:\n\n"
    summary += f"Cash Balance: ${account.balance:.2f}\n\n"
    summary += "Holdings:\n"
    
    for symbol, quantity in holdings.items():
        price = get_share_price(symbol)
        value = price * quantity
        summary += f"- {symbol}: {quantity} shares at ${price:.2f} each = ${value:.2f}\n"
    
    summary += f"\nTotal Portfolio Value: ${total_value:.2f}\n"
    if profit_loss >= 0:
        summary += f"Profit: ${profit_loss:.2f}"
    else:
        summary += f"Loss: ${-profit_loss:.2f}"
    
    return summary

def get_transaction_history():
    """Get the user's transaction history."""
    global account
    if account is None:
        return "Please create an account first."
    
    transactions = account.get_transaction_history()
    if not transactions:
        return "No transactions recorded yet."
    
    # Create a pandas DataFrame for display
    data = []
    for trans_type, symbol, quantity, price in transactions:
        if trans_type in ["DEPOSIT", "WITHDRAW"]:
            data.append({
                "Type": trans_type,
                "Amount": f"${price:.2f}",
                "Symbol": "-",
                "Quantity": "-",
                "Price": "-",
                "Total": f"${price:.2f}"
            })
        else:
            total = price * quantity
            data.append({
                "Type": trans_type,
                "Amount": "-",
                "Symbol": symbol,
                "Quantity": quantity,
                "Price": f"${price:.2f}",
                "Total": f"${total:.2f}"
            })
    
    df = pd.DataFrame(data)
    return df

def available_stocks():
    """Show available stock symbols and prices."""
    stocks = ["AAPL", "TSLA", "GOOGL"]
    info = "Available Stocks:\n"
    for symbol in stocks:
        price = get_share_price(symbol)
        info += f"- {symbol}: ${price:.2f}\n"
    return info

def reset_simulator():
    """Reset the simulator by clearing the account."""
    global account
    account = None
    return "Simulator reset. Please create a new account to start over."

# Create the Gradio interface
with gr.Blocks(title="Trading Simulator") as demo:
    gr.Markdown("# Trading Simulator")
    gr.Markdown("This is a simple trading simulation platform where you can manage an account, buy and sell shares.")
    
    with gr.Tab("Account Management"):
        with gr.Group():
            gr.Markdown("### Create Account")
            with gr.Row():
                user_id_input = gr.Textbox(label="User ID")
                initial_deposit_input = gr.Textbox(label="Initial Deposit ($)")
            create_btn = gr.Button("Create Account")
            create_output = gr.Textbox(label="Result")
            create_btn.click(create_account, inputs=[user_id_input, initial_deposit_input], outputs=create_output)
        
        with gr.Group():
            gr.Markdown("### Deposit/Withdraw Funds")
            with gr.Row():
                amount_input = gr.Textbox(label="Amount ($)")
                deposit_btn = gr.Button("Deposit")
                withdraw_btn = gr.Button("Withdraw")
            funds_output = gr.Textbox(label="Result")
            deposit_btn.click(deposit_funds, inputs=amount_input, outputs=funds_output)
            withdraw_btn.click(withdraw_funds, inputs=amount_input, outputs=funds_output)
    
    with gr.Tab("Trading"):
        with gr.Row():
            stocks_info = gr.Textbox(label="Stock Information", value=available_stocks())
            refresh_btn = gr.Button("Refresh Stock Info")
        refresh_btn.click(available_stocks, inputs=None, outputs=stocks_info)
        
        with gr.Group():
            gr.Markdown("### Buy/Sell Shares")
            with gr.Row():
                symbol_input = gr.Textbox(label="Stock Symbol")
                quantity_input = gr.Textbox(label="Quantity")
            with gr.Row():
                buy_btn = gr.Button("Buy Shares")
                sell_btn = gr.Button("Sell Shares")
            trading_output = gr.Textbox(label="Result")
            buy_btn.click(buy_shares, inputs=[symbol_input, quantity_input], outputs=trading_output)
            sell_btn.click(sell_shares, inputs=[symbol_input, quantity_input], outputs=trading_output)
    
    with gr.Tab("Portfolio"):
        portfolio_btn = gr.Button("View Portfolio Summary")
        portfolio_output = gr.Textbox(label="Portfolio Summary")
        portfolio_btn.click(get_portfolio_summary, inputs=None, outputs=portfolio_output)
    
    with gr.Tab("Transaction History"):
        history_btn = gr.Button("View Transaction History")
        history_output = gr.DataFrame(label="Transaction History")
        history_btn.click(get_transaction_history, inputs=None, outputs=history_output)
    
    with gr.Tab("Simulator Control"):
        reset_btn = gr.Button("Reset Simulator")
        reset_output = gr.Textbox(label="Reset Result")
        reset_btn.click(reset_simulator, inputs=None, outputs=reset_output)

if __name__ == "__main__":
    demo.launch()