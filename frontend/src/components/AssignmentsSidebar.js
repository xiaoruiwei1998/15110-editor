// src/components/AssignmentsSidebar.js
import React from 'react';

const AssignmentsSidebar = ({ assignments, onSelect }) => {
  return (
    <div className="sidebar assignments-sidebar">
      <h3>Assignments</h3>
      {assignments.map((week, index) => (
        <div key={index} className="week">
          <h4>Week {week.week}</h4>
          <ul>
            {week.assignments.map((assignment, idx) => (
              <li key={idx} onClick={() => onSelect(assignment)}>
                {assignment}
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
};

export default AssignmentsSidebar;
