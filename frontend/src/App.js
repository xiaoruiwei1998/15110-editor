import React, { useEffect, useState } from 'react';
import './App.css';
import icona from './assets/icona.png';
import iconb from './assets/iconb.png';
import Assignment from './components/Assignment';
import AssignmentsSidebar from './components/AssignmentsSidebar';
import FileEditor from './components/FileEditor';
import FilesSidebar from './components/FilesSidebar';
import Hints from './components/Hints';
import Output from './components/Output';

const assignmentsData = [
  { week: 1, assignments: ['Lab1', 'Lab2', 'Programming Activity 1', 'Programming Activity 2', 'Problem Set 1', 'Problem Set 2'] },
  { week: 2, assignments: ['Lab3', 'Lab4', 'Programming Activity 3', 'Programming Activity 4', 'Problem Set 3', 'Problem Set 4'] },
  // Add more weeks and assignments as needed
];

const filesData = ['Background.js', 'utils.ts', 'index.css', 'Tic-tac-toe.py', 'App.js', 'SetupTests.js'];

function App() {
  const [selectedAssignment, setSelectedAssignment] = useState(null);
  const [selectedFile, setSelectedFile] = useState('Background.js'); // Default selected file
  const [openFiles, setOpenFiles] = useState(['Background.js']); // Default open file
  const [fileContent, setFileContent] = useState('// Content of Background.js'); // Default content
  const [testResult, setTestResult] = useState('');
  const [output, setOutput] = useState('');
  const [showAssignmentsSidebar, setShowAssignmentsSidebar] = useState(false);
  const [showFilesSidebar, setShowFilesSidebar] = useState(true); // Default to show file sidebar

  const handleEditorChange = (value) => {
    setFileContent(value);
  };

  const handleFileSelect = (file) => {
    setSelectedFile(file);
    if (!openFiles.includes(file)) {
      setOpenFiles([...openFiles, file]);
    }
    // Load the file content here, for now we use a placeholder
    setFileContent('// Content of ' + file);
  };

  const handleCloseFile = (file) => {
    setOpenFiles(openFiles.filter(f => f !== file));
    if (selectedFile === file) {
      setSelectedFile(openFiles.length > 1 ? openFiles[0] : null);
      setFileContent(openFiles.length > 1 ? '// Content of ' + openFiles[0] : '// Your code here');
    }
  };

  const runCode = () => {
    try {
      // Get the content from the current editor instance
      // const currentContent = editorRef.current.getValue();

      // Capture console.log output
      let capturedOutput = '';
      const originalLog = console.log;
      console.log = (...args) => {
        capturedOutput += args.join(' ') + '\n';
        originalLog.apply(console, args);
      };

      // Execute the code
      eval(fileContent);

      // Restore original console.log
      console.log = originalLog;
      setOutput(capturedOutput);
      console.log(capturedOutput);
    } catch (error) {
      setOutput(`Error: ${error.message}`);
    }
  };

  const generateOrGetUserId = () => {
    let userId = localStorage.getItem('uid');
    if (!userId) {
      userId = Math.random().toString(36).substring(7);
      localStorage.setItem('uid', userId);
    }
  }

  useEffect(() => {
    generateOrGetUserId(); 
  }, []);

  return (
    <div className="app">
      <div className="main-content">
        {showAssignmentsSidebar && (
          <div className="left-sidebar">
            <AssignmentsSidebar assignments={assignmentsData} onSelect={setSelectedAssignment} />
          </div>
        )}
        <div className="left-pane">
          <div className="top-bar">
            <button className="top-bar-button" onClick={() => setShowAssignmentsSidebar(!showAssignmentsSidebar)}>
              <img src={icona} className="iconimg" alt="icon" />
              Assignments
            </button>
          </div>
          <div className="assignments">
            <Assignment />
          </div>
          <div className="hints-section">
            <Hints
              fileContent={fileContent}
            />
          </div>
        </div>
        <div className="right-pane">
          <div className="top-bar">
            <button className="top-bar-button" onClick={() => setShowFilesSidebar(!showFilesSidebar)}>
              <img src={iconb} className="iconimg" alt="icon" />
              Files
            </button>
            <div className="sub-top-bar">
              <button className="sub-top-bar button" onClick={runCode}>Run</button>
              <button className="sub-top-bar button" onClick={runCode}>Submit</button>
            </div>
          </div>
          <div className="code-panel">
            <div className="code-left-pane">
              {showFilesSidebar && (
                <div className="files-sidebar">
                  <FilesSidebar files={filesData} onSelect={handleFileSelect} />
                </div>
              )}
            </div>
            <div className="code-right-pane">
              <FileEditor
                openFiles={openFiles}
                currentFile={selectedFile}
                content={fileContent}
                onChange={handleEditorChange}
                onSelect={handleFileSelect}
                onClose={handleCloseFile}
              />
            </div>
          </div>
          <Output result={testResult} output={output} />
        </div>
      </div>
    </div>
  );
}

export default App;
