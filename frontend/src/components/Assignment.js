import React, { useState } from 'react';

const Assignment = () => {
  const [activeSection, setActiveSection] = useState('description');

  const showSection = (section) => {
    setActiveSection(section);
  };

  return (
    <div className="assignment">
      <div className="navbar">
        <button
          className={activeSection === 'description' ? 'active' : ''}
          onClick={() => showSection('description')}
        >
          Description
        </button>
        <button
          className={activeSection === 'output' ? 'active' : ''}
          onClick={() => showSection('output')}
        >
          Output
        </button>
        <button
          className={activeSection === 'test-cases' ? 'active' : ''}
          onClick={() => showSection('test-cases')}
        >
          Test Cases
        </button>
      </div>

      <div className="content">
        <div className={`assignment-section ${activeSection === 'description' ? 'active' : ''}`}>
          <h2>Lab 11</h2>
          <h3>Overview Of Tic-Tac-Toe</h3>
          <p>
            In this lab, you will develop a program that allows two players to play Tic-Tac-Toe.
            Players alternate placing their marks, X's and O's, respectively in the cells of a 3x3 grid.
            The first player to place three of their marks in a vertical, horizontal, or diagonal line is the winner.
            If no lines are formed, the game ends in a tie.
          </p>
        </div>
        <div className={`assignment-section ${activeSection === 'output' ? 'active' : ''}`}>
          <h2>Output</h2>
          <p>This page will display the output of your tic-tac-toe program...</p>
        </div>
        <div className={`assignment-section ${activeSection === 'test-cases' ? 'active' : ''}`}>
          <h2>Test Cases</h2>
          <p>This page will provide the test cases for your tic-tac-toe program...</p>
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
        .assignment-section {
          display: none;
        }
        .assignment-section.active {
          display: block;
        }
      `}</style>
    </div>
  );
};

export default Assignment;
