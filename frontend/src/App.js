import React, { useState, useEffect } from 'react';
import axios from 'axios';

function App() {
  const [message, setMessage] = useState('');

  useEffect(() => {
    // Test connection to backend
    axios.get(process.env.REACT_APP_API_URL + '/')
      .then(response => {
        setMessage(response.data.message);
      })
      .catch(error => {
        console.error('Error connecting to backend:', error);
        setMessage('Error connecting to backend');
      });
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <h1>ShareFoods</h1>
        <p>Backend Status: {message}</p>
      </header>
    </div>
  );
}

export default App;