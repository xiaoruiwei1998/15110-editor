import React from 'react';
import jsIcon from '../assets/jsIcon.png';
import tsIcon from '../assets/tsIcon.png';
import cssIcon from '../assets/cssIcon.png';
import pyIcon from '../assets/pyIcon.png';

const fileIcons = {
  js: jsIcon,
  ts: tsIcon,
  css: cssIcon,
  py: pyIcon,
};

const getFileIcon = (file) => {
  const ext = file.split('.').pop();
  return fileIcons[ext] || null; // 如果找不到图标可以返回 null 或者默认图标
};

const FilesSidebar = ({ files, onSelect }) => {
  return (
    <div className="sidebar files-sidebar">
      <ul>
        {files.map((file, index) => (
          <li key={index} onClick={() => onSelect(file)}>
            <img src={getFileIcon(file)} alt={`${file} icon`} className="iconimg" />
            {file}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default FilesSidebar;
