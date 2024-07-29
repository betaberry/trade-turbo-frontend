import React from 'react';
import { useParams } from 'react-router-dom';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './Insight.css';

const Insight = () => {
  const { stockName } = useParams();

  const stockData = [
    { date: "2024-07-26", open: 190.5100, high: 193.5700, low: 189.6220, close: 191.7500, volume: 4294875 },
    { date: "2024-07-25", open: 186.8000, high: 196.2600, low: 185.3000, close: 191.9800, volume: 9532802 },
    { date: "2024-07-24", open: 184.1400, high: 185.0714, low: 183.1450, close: 184.0200, volume: 6962071 },
    // Add more data points as needed
  ];

  
  const reversedStockData = [...stockData].reverse();

  return (
    <div className="insight-container">
      <h1>{stockName} Insight</h1>
      <ResponsiveContainer width="100%" height={400}>
        <LineChart
          data={reversedStockData}
          margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="close" stroke="#8884d8" activeDot={{ r: 8 }} />
        </LineChart>
      </ResponsiveContainer>
      <table className="insight-table">
        <thead>
          <tr>
            <th>Date</th>
            <th>Open</th>
            <th>High</th>
            <th>Low</th>
            <th>Close</th>
            <th>Volume</th>
          </tr>
        </thead>
        <tbody>
          {stockData.map((data) => (
            <tr key={data.date}>
              <td>{data.date}</td>
              <td>{data.open.toFixed(2)}</td>
              <td>{data.high.toFixed(2)}</td>
              <td>{data.low.toFixed(2)}</td>
              <td>{data.close.toFixed(2)}</td>
              <td>{data.volume}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default Insight;
