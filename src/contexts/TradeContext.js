import React, { createContext, useState } from 'react';

export const TradeContext = createContext();

export const TradeProvider = ({ children }) => {
  const [trades, setTrades] = useState([]);
  const [assets, setAssets] = useState({
    balance: 100000, // initial balance
    stocks: {
      Apple: 0,
      Tesla: 0,
      Google: 0,
      Amazon: 0,
      Nike: 0,
    },
  });

  const addTrade = (trade) => {
    setTrades([...trades, trade]);

    // Update assets based on trade
    const updatedStocks = { ...assets.stocks };
    const newBalance = assets.balance;

    if (trade.action === 'buy') {
      updatedStocks[trade.stockName] += trade.amount / trade.price;
      newBalance -= trade.amount;
    } else {
      updatedStocks[trade.stockName] -= trade.amount / trade.price;
      newBalance += trade.amount;
    }

    setAssets({ balance: newBalance, stocks: updatedStocks });
  };

  return (
    <TradeContext.Provider value={{ trades, assets, addTrade }}>
      {children}
    </TradeContext.Provider>
  );
};
