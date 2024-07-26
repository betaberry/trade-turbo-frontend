import React from 'react';
import './Dashboard.css';

const Dashboard = () => {
  // Mock data for user and stock details
  const user = {
    username: 'JohnDoe',
    walletBalance: 1000,
    stockAsset: 5000,
    totalPNL: 1500,
    balance: 2000,
  };

  const stocks = [
    { name: 'Apple', purchasePrice: 150, currentPrice: 160, pnl: 10 },
    { name: 'Tesla', purchasePrice: 700, currentPrice: 680, pnl: -20 },
    { name: 'Google', purchasePrice: 2500, currentPrice: 2600, pnl: 100 },
    { name: 'Amazon', purchasePrice: 3300, currentPrice: 3400, pnl: 100 },
    { name: 'Nike', purchasePrice: 130, currentPrice: 120, pnl: -10 },
  ];

  return (
    <div className="dashboard-container">
      <h1>Dashboard</h1>
      <div className="user-info">
        <div className="user-info-item">
          <strong>Username:</strong> {user.username}
        </div>
        <div className="user-info-item">
          <strong>Total Asset:</strong> ${user.walletBalance + user.stockAsset}
        </div>
        <div className="user-info-item">
          <strong>Balance:</strong> ${user.balance}
        </div>
        <div className="user-info-item">
          <strong>Total PNL:</strong> ${user.totalPNL}
        </div>
      </div>
      <table className="stocks-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Purchase Price</th>
            <th>Current Price</th>
            <th>PNL</th>
          </tr>
        </thead>
        <tbody>
          {stocks.map((stock, index) => (
            <tr key={index}>
              <td>{stock.name}</td>
              <td>${stock.purchasePrice.toFixed(2)}</td>
              <td>${stock.currentPrice.toFixed(2)}</td>
              <td className={stock.pnl >= 0 ? 'positive' : 'negative'}>
                {stock.pnl >= 0 ? '+' : ''}${stock.pnl.toFixed(2)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default Dashboard;
