from lumibot.brokers import Alpaca
from lumibot.backtesting import YahooDataBacktesting
from lumibot.strategies.strategy import Strategy
from lumibot.traders import Trader
from datetime import datetime 
from alpaca_trade_api import REST 
from timedelta import Timedelta 
from finbert_utils import estimate_sentiment
API_KEY="c0266de142229f47e76e950967557d48a54b78b302626620d1fef609f93b56f1" # REDACTED WITH SHA256 FOR PRIVACY REASONS
API_SECRET="6aa23fbb31edcc05fe70ef790e4a2443c5cd8280e90a2286a7ccb639d6d5a50e" # REDACTED WITH SHA256 FOR PRIVACY REASONS
BASE_URL="https://paper-api.alpaca.markets"
ALPACA_CREDS={"API_KEY":API_KEY,"API_SECRET":API_SECRET,"PAPER": True}
class MLTrader(Strategy): 
    def initialize(self,symbol:str="SPY",cash_at_risk:float=.5): 
        self.symbol=symbol
        self.sleeptime="24H" 
        self.last_trade=None 
        self.cash_at_risk=cash_at_risk
        self.api=REST(base_url=BASE_URL,key_id=API_KEY,secret_key=API_SECRET)
    def position_sizing(self): 
        cash=self.get_cash() 
        last_price=self.get_last_price(self.symbol)
        quantity=round(cash*self.cash_at_risk/last_price,0)
        return cash,last_price,quantity
    def get_dates(self): 
        today=self.get_datetime()
        three_days_prior=today-Timedelta(days=3)
        return today.strftime('%Y-%m-%d'),three_days_prior.strftime('%Y-%m-%d')
    def get_sentiment(self): 
        today,three_days_prior=self.get_dates()
        news=self.api.get_news(symbol=self.symbol,start=three_days_prior,end=today)
        news=[ev.__dict__["_raw"]["headline"] for ev in news]
        probability,sentiment=estimate_sentiment(news)
        return probability,sentiment
    def on_trading_iteration(self):
        cash,last_price,quantity=self.position_sizing() 
        probability,sentiment=self.get_sentiment()
        if cash>last_price: 
            if sentiment=="positive" and probability>.999: 
                if self.last_trade=="sell":self.sell_all() 
                order=self.create_order(self.symbol,quantity,"buy",type="bracket",take_profit_price=last_price*1.20,stop_loss_price=last_price*.95)
                self.submit_order(order) 
                self.last_trade="buy"
            elif sentiment=="negative" and probability>.999: 
                if self.last_trade=="buy":self.sell_all() 
                order=self.create_order(self.symbol,quantity,"sell",type="bracket",take_profit_price=last_price*.8,stop_loss_price=last_price*1.05)
                self.submit_order(order) 
                self.last_trade="sell"
start_date=datetime(2020,4,1) # POST-COVID DATE
end_date=datetime(9999,12,31) # CURRENT
broker=Alpaca(ALPACA_CREDS) 
strategy=MLTrader(name='mlstrat',broker=broker,parameters={"symbol":"AAPL","cash_at_risk":1}) # AAPL IS EXAMPLE STOCK, REPLACE WITH PREFERRED STOCK!
strategy.backtest(YahooDataBacktesting,start_date,end_date,parameters={"symbol":"AAPL","cash_at_risk":1}) # AAPL IS EXAMPLE STOCK, REPLACE WITH PREFERRED STOCK!
trader=Trader()
trader.add_strategy(strategy)
trader.run_all()