def get_share_price(symbol):
    """Test implementation that returns fixed prices for AAPL, TSLA, GOOGL."""
    prices = {
        'AAPL': 150.0,
        'TSLA': 800.0,
        'GOOGL': 2500.0
    }
    return prices.get(symbol, 0.0)

class Account:
    def __init__(self, user_id: str, initial_deposit: float) -> None:
        """
        Initialize a new account with user ID and initial deposit.
        
        Args:
            user_id: A unique identifier for the user
            initial_deposit: The initial amount to deposit
        """
        if initial_deposit <= 0:
            raise ValueError("Initial deposit must be positive")
            
        self.user_id = user_id
        self.balance = initial_deposit
        self.holdings = {}  # Map of stock symbol to quantity
        self.transactions = []  # List of (type, symbol, quantity, price) tuples
        self.initial_deposit = initial_deposit
    
    def deposit(self, amount: float) -> bool:
        """
        Add funds to the account balance.
        
        Args:
            amount: The amount to deposit
            
        Returns:
            True if successful, False otherwise
        """
        if amount <= 0:
            return False
            
        self.balance += amount
        self.transactions.append(("DEPOSIT", "", 0, amount))
        return True
    
    def withdraw(self, amount: float) -> bool:
        """
        Subtract funds from the account balance.
        
        Args:
            amount: The amount to withdraw
            
        Returns:
            True if successful, False otherwise
        """
        if amount <= 0 or amount > self.balance:
            return False
            
        self.balance -= amount
        self.transactions.append(("WITHDRAW", "", 0, amount))
        return True
    
    def buy_shares(self, symbol: str, quantity: int) -> bool:
        """
        Record a purchase of shares.
        
        Args:
            symbol: The stock symbol
            quantity: The number of shares to buy
            
        Returns:
            True if successful, False otherwise
        """
        if quantity <= 0:
            return False
            
        price = get_share_price(symbol)
        if price == 0.0:  # Invalid symbol
            return False
            
        total_cost = price * quantity
        if total_cost > self.balance:
            return False
            
        self.balance -= total_cost
        
        # Update holdings
        if symbol in self.holdings:
            self.holdings[symbol] += quantity
        else:
            self.holdings[symbol] = quantity
            
        self.transactions.append(("BUY", symbol, quantity, price))
        return True
    
    def sell_shares(self, symbol: str, quantity: int) -> bool:
        """
        Record a sale of shares.
        
        Args:
            symbol: The stock symbol
            quantity: The number of shares to sell
            
        Returns:
            True if successful, False otherwise
        """
        if quantity <= 0 or symbol not in self.holdings or self.holdings[symbol] < quantity:
            return False
            
        price = get_share_price(symbol)
        if price == 0.0:  # Invalid symbol
            return False
            
        total_value = price * quantity
        
        self.balance += total_value
        self.holdings[symbol] -= quantity
        
        # Remove the symbol from holdings if quantity becomes 0
        if self.holdings[symbol] == 0:
            del self.holdings[symbol]
            
        self.transactions.append(("SELL", symbol, quantity, price))
        return True
    
    def get_portfolio_value(self) -> float:
        """
        Calculate the total value of the user's portfolio.
        
        Returns:
            The total value of all holdings plus cash balance
        """
        holdings_value = sum(get_share_price(symbol) * quantity 
                           for symbol, quantity in self.holdings.items())
        return self.balance + holdings_value
    
    def get_profit_or_loss(self) -> float:
        """
        Calculate the profit or loss since the initial deposit.
        
        Returns:
            The profit (positive) or loss (negative) amount
        """
        return self.get_portfolio_value() - self.initial_deposit
    
    def get_holdings(self) -> dict:
        """
        Get the user's current stock holdings.
        
        Returns:
            A dictionary mapping stock symbols to quantities
        """
        return self.holdings.copy()
    
    def get_transaction_history(self) -> list:
        """
        Get the user's transaction history.
        
        Returns:
            A list of transactions as (type, symbol, quantity, price) tuples
        """
        return self.transactions.copy()