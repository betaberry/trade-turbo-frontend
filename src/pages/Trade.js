import React, { useState } from 'react';
import './Trade.css';

const Trade = () => {
  const [stockName, setStockName] = useState('');
  const [stockPrice, setStockPrice] = useState('');
  const [orderType, setOrderType] = useState('buy'); // 'buy' or 'sell'
  const [amount, setAmount] = useState('');

  const handleConfirm = () => {
    // Handle order confirmation logic here
    console.log(`Order: ${orderType} ${amount} of ${stockName} at ${stockPrice}`);
  };

  return (
    <div className="trade-container">
      <h1>Place Order</h1>
      <div className="trade-input">
        <label htmlFor="stock-name">Stock Name:</label>
        <input
          type="text"
          id="stock-name"
          value={stockName}
          onChange={(e) => setStockName(e.target.value)}
        />
      </div>
      <div className="trade-input">
        <label htmlFor="stock-price">Stock Price:</label>
        <input
          type="text"
          id="stock-price"
          value={stockPrice}
          onChange={(e) => setStockPrice(e.target.value)}
        />
      </div>
      <div className="trade-buttons">
        <button
          className={orderType === 'buy' ? 'active' : ''}
          onClick={() => setOrderType('buy')}
        >
          Buy
        </button>
        <button
          className={orderType === 'sell' ? 'active' : ''}
          onClick={() => setOrderType('sell')}
        >
          Sell
        </button>
      </div>
      <div className="trade-input">
        <label htmlFor="amount">Amount:</label>
        <input
          type="number"
          id="amount"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
        />
      </div>
      <button className="confirm-button" onClick={handleConfirm}>
        Confirm
      </button>
    </div>
  );
};

export default Trade;
