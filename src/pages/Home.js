import React, { useState } from 'react';
import './Home.css';

const Home = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortConfig, setSortConfig] = useState({ key: 'name', direction: 'ascending' });

  const stocks = [
    { name: 'Apple', price: 150.00 },
    { name: 'Tesla', price: 700.00 },
    { name: 'Google', price: 2500.00 },
    { name: 'Amazon', price: 3300.00 },
    { name: 'Nike', price: 130.00 },
  ];

  const handleSearch = (e) => {
    setSearchTerm(e.target.value);
  };

  const handleSort = (key) => {
    let direction = 'ascending';
    if (sortConfig.key === key && sortConfig.direction === 'ascending') {
      direction = 'descending';
    }
    setSortConfig({ key, direction });
  };

  const sortedStocks = [...stocks].sort((a, b) => {
    if (sortConfig.key === 'price') {
      if (a.price < b.price) {
        return sortConfig.direction === 'ascending' ? -1 : 1;
      }
      if (a.price > b.price) {
        return sortConfig.direction === 'ascending' ? 1 : -1;
      }
    } else {
      if (a[sortConfig.key].toLowerCase() < b[sortConfig.key].toLowerCase()) {
        return sortConfig.direction === 'ascending' ? -1 : 1;
      }
      if (a[sortConfig.key].toLowerCase() > b[sortConfig.key].toLowerCase()) {
        return sortConfig.direction === 'ascending' ? 1 : -1;
      }
    }
    return 0;
  });

  const filteredStocks = sortedStocks.filter(stock =>
    stock.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="home-container">
      <h1>Stocks Overview</h1>
      <div className="search-bar">
        <input
          type="text"
          placeholder="Search stocks"
          value={searchTerm}
          onChange={handleSearch}
        />
        <button className="search-button">Search</button>
      </div>
      <table className="stocks-table">
        <thead>
          <tr>
            <th onClick={() => handleSort('name')}>
              Name {sortConfig.key === 'name' ? (sortConfig.direction === 'ascending' ? '▲' : '▼') : ''}
            </th>
            <th onClick={() => handleSort('price')}>
              Price {sortConfig.key === 'price' ? (sortConfig.direction === 'ascending' ? '▲' : '▼') : ''}
            </th>
          </tr>
        </thead>
        <tbody>
          {filteredStocks.map((stock, index) => (
            <tr key={index}>
              <td>{stock.name}</td>
              <td>${stock.price.toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default Home;
