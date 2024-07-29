// src/components/Output.js
/*import React from 'react';
const Output = ({ result, output }) => {
  return (
    <div className="output">
      <h3>Test Result</h3>
      <div>{result}</div>
      <h3>Output</h3>
      <div>{output}</div>
    </div>
  );
};

export default Output;*/

import React, { useState } from 'react';

const Output = () => {
  const [activeSection, setActiveSection] = useState('output');

  const showSection = (section) => {
    setActiveSection(section);
  };

  return (
    <div className="output">
      <div className="navbar">
        <button
          className={activeSection === 'output' ? 'active' : ''}
          onClick={() => showSection('output')}
        >
          Output
        </button>
        <button
          className={activeSection === 'test-results' ? 'active' : ''}
          onClick={() => showSection('test-results')}
        >
          Test Results
        </button>
      </div>

      <div className="content">
        <div className={`output-section ${activeSection === 'output' ? 'active' : ''}`}>
          <h2>Output</h2>
          <p>This page will display the output of your program...</p>
        </div>
        <div className={`output-section ${activeSection === 'test-results' ? 'active' : ''}`}>
          <h2>Test Results</h2>
          <p>This page will display the test results of your program...</p>
        </div>
      </div>

      <style jsx>{`
        .navbar {
          overflow: hidden;
          background-color: transparent;
          border-bottom: 1px solid #979BA1;
        }
        .navbar button {
          position: relative;
          float: left;
          display: block;
          text-align: center;
          font-weight: lighter;
          padding: 14px 16px;
          text-decoration: none;
          background: none;
          border: none;
          cursor: pointer;
          color: #000;
        }
        .navbar button.active,
        .navbar button:hover {
          color: #4682B4;
          text-decoration: underline;
          text-decoration-color: #4682B4;
          text-decoration-thickness: 5px;
          text-underline-offset: 16px;
        }
        .content {
          padding: 20px;
        }
        .output-section {
          display: none;
        }
        .output-section.active {
          display: block;
        }
      `}</style>
    </div>
  );
};

export default Output;

