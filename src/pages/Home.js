import React, { useState } from 'react';
import './Home.css';

const Home = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const stocks = [
    { name: 'Apple', price: '$150.00' },
    { name: 'Tesla', price: '$700.00' },
    { name: 'Google', price: '$2,500.00' },
    { name: 'Amazon', price: '$3,300.00' },
    { name: 'Nike', price: '$130.00' },
  ];

  const filteredStocks = stocks.filter(stock =>
    stock.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleSearch = (e) => {
    setSearchTerm(e.target.value);
  };

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
            <th>Name</th>
            <th>Price</th>
          </tr>
        </thead>
        <tbody>
          {filteredStocks.map((stock, index) => (
            <tr key={index}>
              <td>{stock.name}</td>
              <td>{stock.price}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default Home;
