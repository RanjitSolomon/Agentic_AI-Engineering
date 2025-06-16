import unittest
from unittest.mock import patch
from accounts import Account, get_share_price

class TestGetSharePrice(unittest.TestCase):
    """Test the get_share_price function."""
    
    def test_valid_symbols(self):
        """Test that valid stock symbols return the correct prices."""
        self.assertEqual(get_share_price("AAPL"), 150.0)
        self.assertEqual(get_share_price("TSLA"), 800.0)
        self.assertEqual(get_share_price("GOOGL"), 2500.0)
    
    def test_invalid_symbol(self):
        """Test that invalid stock symbols return 0.0."""
        self.assertEqual(get_share_price("INVALID"), 0.0)
        self.assertEqual(get_share_price(""), 0.0)
        self.assertEqual(get_share_price(None), 0.0)

class TestAccount(unittest.TestCase):
    """Test the Account class."""
    
    def setUp(self):
        """Set up a test account before each test."""
        self.account = Account("test_user", 10000.0)
    
    def test_init(self):
        """Test account initialization."""
        # Test valid initialization
        account = Account("user1", 5000.0)
        self.assertEqual(account.user_id, "user1")
        self.assertEqual(account.balance, 5000.0)
        self.assertEqual(account.initial_deposit, 5000.0)
        self.assertEqual(account.holdings, {})
        self.assertEqual(account.transactions, [])
        
        # Test initialization with invalid deposit
        with self.assertRaises(ValueError):
            Account("user2", 0)
        with self.assertRaises(ValueError):
            Account("user3", -100)
    
    def test_deposit(self):
        """Test depositing funds."""
        # Test valid deposit
        self.assertTrue(self.account.deposit(500.0))
        self.assertEqual(self.account.balance, 10500.0)
        
        # Test invalid deposit amounts
        self.assertFalse(self.account.deposit(0))
        self.assertFalse(self.account.deposit(-100))
        
        # Check transaction was recorded
        self.assertEqual(len(self.account.transactions), 1)
        self.assertEqual(self.account.transactions[0], ("DEPOSIT", "", 0, 500.0))
    
    def test_withdraw(self):
        """Test withdrawing funds."""
        # Test valid withdrawal
        self.assertTrue(self.account.withdraw(1000.0))
        self.assertEqual(self.account.balance, 9000.0)
        
        # Test withdrawing too much
        self.assertFalse(self.account.withdraw(10000.0))
        
        # Test invalid withdrawal amounts
        self.assertFalse(self.account.withdraw(0))
        self.assertFalse(self.account.withdraw(-100))
        
        # Check transaction was recorded
        self.assertEqual(len(self.account.transactions), 1)
        self.assertEqual(self.account.transactions[0], ("WITHDRAW", "", 0, 1000.0))
    
    def test_buy_shares(self):
        """Test buying shares."""
        # Test buying valid shares
        self.assertTrue(self.account.buy_shares("AAPL", 10))
        self.assertEqual(self.account.balance, 8500.0)  # 10000 - (150 * 10)
        self.assertEqual(self.account.holdings, {"AAPL": 10})
        
        # Test buying more of the same shares
        self.assertTrue(self.account.buy_shares("AAPL", 5))
        self.assertEqual(self.account.balance, 7750.0)  # 8500 - (150 * 5)
        self.assertEqual(self.account.holdings, {"AAPL": 15})
        
        # Test buying different shares
        self.assertTrue(self.account.buy_shares("TSLA", 2))
        self.assertEqual(self.account.balance, 6150.0)  # 7750 - (800 * 2)
        self.assertEqual(self.account.holdings, {"AAPL": 15, "TSLA": 2})
        
        # Test buying invalid quantity
        self.assertFalse(self.account.buy_shares("AAPL", 0))
        self.assertFalse(self.account.buy_shares("AAPL", -5))
        
        # Test buying invalid symbol
        self.assertFalse(self.account.buy_shares("INVALID", 10))
        
        # Test buying more than can afford
        self.assertFalse(self.account.buy_shares("GOOGL", 3))  # 2500 * 3 > 6150
        
        # Check transactions were recorded
        self.assertEqual(len(self.account.transactions), 3)
        self.assertEqual(self.account.transactions[0], ("BUY", "AAPL", 10, 150.0))
        self.assertEqual(self.account.transactions[1], ("BUY", "AAPL", 5, 150.0))
        self.assertEqual(self.account.transactions[2], ("BUY", "TSLA", 2, 800.0))
    
    def test_sell_shares(self):
        """Test selling shares."""
        # Setup: buy some shares first
        self.account.buy_shares("AAPL", 10)
        self.account.buy_shares("TSLA", 5)
        
        # Reset the transactions list for cleaner testing
        self.account.transactions = []
        initial_balance = self.account.balance
        
        # Test selling some shares
        self.assertTrue(self.account.sell_shares("AAPL", 3))
        self.assertEqual(self.account.balance, initial_balance + 150.0 * 3)
        self.assertEqual(self.account.holdings["AAPL"], 7)
        
        # Test selling all remaining shares of a symbol
        self.assertTrue(self.account.sell_shares("AAPL", 7))
        self.assertNotIn("AAPL", self.account.holdings)
        
        # Test selling more than owned
        self.assertFalse(self.account.sell_shares("TSLA", 10))
        
        # Test selling invalid quantity
        self.assertFalse(self.account.sell_shares("TSLA", 0))
        self.assertFalse(self.account.sell_shares("TSLA", -1))
        
        # Test selling unowned symbol
        self.assertFalse(self.account.sell_shares("GOOGL", 1))
        
        # Check transactions were recorded
        self.assertEqual(len(self.account.transactions), 2)
        self.assertEqual(self.account.transactions[0], ("SELL", "AAPL", 3, 150.0))
        self.assertEqual(self.account.transactions[1], ("SELL", "AAPL", 7, 150.0))
    
    def test_get_portfolio_value(self):
        """Test calculating portfolio value."""
        # Initial portfolio value should equal balance
        self.assertEqual(self.account.get_portfolio_value(), 10000.0)
        
        # Buy some shares and test again
        self.account.buy_shares("AAPL", 10)  # 10 * 150 = 1500
        self.account.buy_shares("TSLA", 2)   # 2 * 800 = 1600
        
        expected_value = self.account.balance + 1500 + 1600
        self.assertEqual(self.account.get_portfolio_value(), expected_value)
    
    def test_get_profit_or_loss(self):
        """Test calculating profit or loss."""
        # Initially there should be no profit or loss
        self.assertEqual(self.account.get_profit_or_loss(), 0.0)
        
        # Simulate some trading activity
        self.account.buy_shares("AAPL", 10)
        self.account.sell_shares("AAPL", 5)  # Sell at the same price, so no profit/loss yet
        
        # Since we bought at market price and sold at market price, profit should be 0
        self.assertEqual(self.account.get_profit_or_loss(), 0.0)
        
        # Now let's mock a price change to test profit calculation
        with patch("accounts.get_share_price", return_value=200.0):
            # With AAPL now at $200, our 5 remaining shares have gained $50 each
            expected_profit = 5 * (200.0 - 150.0)  # 5 shares * $50 gain each
            self.assertEqual(self.account.get_profit_or_loss(), expected_profit)
    
    def test_get_holdings(self):
        """Test getting account holdings."""
        self.assertEqual(self.account.get_holdings(), {})
        
        # Buy some shares
        self.account.buy_shares("AAPL", 10)
        self.account.buy_shares("TSLA", 5)
        
        expected_holdings = {"AAPL": 10, "TSLA": 5}
        self.assertEqual(self.account.get_holdings(), expected_holdings)
        
        # Verify that the returned dictionary is a copy
        holdings = self.account.get_holdings()
        holdings["GOOGL"] = 3
        self.assertNotIn("GOOGL", self.account.get_holdings())
    
    def test_get_transaction_history(self):
        """Test getting transaction history."""
        self.assertEqual(self.account.get_transaction_history(), [])
        
        # Perform some transactions
        self.account.deposit(500)
        self.account.buy_shares("AAPL", 2)
        self.account.withdraw(200)
        
        expected_history = [
            ("DEPOSIT", "", 0, 500),
            ("BUY", "AAPL", 2, 150.0),
            ("WITHDRAW", "", 0, 200)
        ]
        self.assertEqual(self.account.get_transaction_history(), expected_history)
        
        # Verify that the returned list is a copy
        history = self.account.get_transaction_history()
        history.append(("FAKE", "", 0, 0))
        self.assertEqual(len(self.account.get_transaction_history()), 3)

if __name__ == "__main__":
    unittest.main()