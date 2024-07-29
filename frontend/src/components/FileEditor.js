import React, { useState, useEffect } from 'react';
import Editor from '@monaco-editor/react';

const FileEditor = ({ openFiles, currentFile, content, onChange, onSelect, onClose }) => {
  const [editorContent, setEditorContent] = useState(content || '');

  useEffect(() => {
    setEditorContent(content || '');
  }, [content]);

  const handleEditorChange = (value) => {
    setEditorContent(value);
    if (onChange) {
      onChange(value);
    }
  };

  return (
    <div className="file-editor">
      <div className="file-name-tabs">
        {openFiles.map((file, index) => (
          <button
            key={index}
            className={`file-name-button ${file === currentFile ? 'active' : ''}`}
            onClick={() => onSelect(file)}
          >
            {file} <span className="close-icon" onClick={(e) => { e.stopPropagation(); onClose(file); }}>X</span>
          </button>
        ))}
      </div>
      <Editor
        height="70vh"
        defaultLanguage="javascript"
        value={editorContent}
        onChange={handleEditorChange}
      />
    </div>
  );
};

export default FileEditor;
