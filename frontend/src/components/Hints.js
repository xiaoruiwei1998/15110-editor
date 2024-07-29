import React, { useState } from 'react';
import userprofile from '../assets/user-profile.png';const Hints = () => {
    const [activeSection, setActiveSection] = useState('hints'); // Tracks which section is active
    const [userInput, setUserInput] = useState(''); // State for main input section
    const [helpInput, setHelpInput] = useState(''); // State for help section input
    const [isFocused, setIsFocused] = useState(false); // Tracks focus state for input styling
    const [showStrategies, setShowStrategies] = useState(false); // Controls visibility of strategies section
    const [strategyColors, setStrategyColors] = useState([]); // Holds colors for strategies section
    const [showPrompt, setShowPrompt] = useState(false); // Controls visibility of prompt section
    const [showHelp, setShowHelp] = useState(false); // Controls visibility of help section
    const [collapsedSections, setCollapsedSections] = useState({}); // Tracks collapsed state of sections
    const [conversation, setConversation] = useState([]); // Holds the conversation in the help section

    const colors = ['#E6F3F0', '#FEF6EA', '#FEFCE8']; // Predefined colors for strategies

    const colorMap = {
        '#E6F3F0': '#007F66',
        '#FEF6EA': '#EE9E27',
        '#FEFCE8': '#FCE200'
    };

    const showSection = (section) => {
        setActiveSection(section);
    };

    const handleInputChange = (event) => {
        setUserInput(event.target.value);
    };

    const handleHelpInputChange = (event) => {
        setHelpInput(event.target.value);
    };

    const handleKeyPress = (event) => {
        if (event.key === 'Enter') {
            updateStrategies();
        }
    };

    const handleHelpKeyPress = (event) => {
        if (event.key === 'Enter') {
            displaySystemResponse();
        }
    };

    const updateStrategies = () => {
        setShowPrompt(false); //prompt section is hidden
        setShowStrategies(false); // Hide old strategies section
        setTimeout(() => {
            setStrategyColors(shuffleArray(colors)); // Shuffle colors and set as strategy colors
            setShowStrategies(true); // Show new strategies section
        }, 0);
    };

    const shuffleArray = (array) => {
        const shuffledArray = array.slice();
        for (let i = shuffledArray.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [shuffledArray[i], shuffledArray[j]] = [shuffledArray[j], shuffledArray[i]];
        }
        return shuffledArray;
    };

    const handleNarrowRightClick = () => {
        setShowStrategies(false); // Ensure strategies section is hidden
        setShowPrompt(true); // Show the prompt section when the button is clicked
    };

    const handleBackClick = () => {
        if (showPrompt) {
            setShowPrompt(false);
            setShowStrategies(true);
        } else if (showStrategies) {
            setShowStrategies(false);
        } else if (showHelp) {
            setShowHelp(false);
            setShowPrompt(true);
        }
    };

    const handleAskForHelpClick = () => {
        setShowPrompt(false);
        setShowHelp(true); // Show the help section when the button is clicked
    };

    const toggleSection = (index) => {
        setCollapsedSections(prevState => ({
            ...prevState,
            [index]: !prevState[index]
        }));
    };

    const displaySystemResponse = () => {
        const response = "In Python, len(nums) - 1 means the length of the list nums minus 1. This is often used to get the index of the last element in the list, as indexing in Python starts from 0. For example, if nums has 5 elements, len(nums) - 1 would be 4, which is the index of the last element in the list.";
        setConversation([...conversation, { user: helpInput, system: response }]); // Add user input and system response to conversation
        setHelpInput(''); // Clear help input field
    };

    const handleResetClick = () => {
        if (window.confirm("Are you sure you want to reset the entire hints process?")) {
            setUserInput('');
            setHelpInput('');
            setConversation([]);
            setShowStrategies(false);
            setShowPrompt(false);
            setShowHelp(false);
            setActiveSection('hints');
        }
    };

    return (
        <div className="hints">
             <div className="navbar">
                <button
                    className={activeSection === 'hints' ? 'active' : ''}
                    onClick={() => showSection('hints')}
                >
                    Hints
                </button>
                {showHelp && (
                    <button className="reset-button" onClick={handleResetClick}>Reset Process</button> // Reset button appears only in help section
                )}
            </div>


            <div className="content">
                <div className={`assignment-section ${activeSection === 'hints' ? 'active' : ''}`}>
                    {!showStrategies && !showPrompt && !showHelp && (
                        <div className='input-section'>
                            <p>Need help? Ask your question here and the AI will help you:</p>
                            <div className={`input-container ${isFocused ? 'focused' : ''}`}>
                                <input
                                    type="text"
                                    value={userInput}
                                    onChange={handleInputChange}
                                    onKeyPress={handleKeyPress}
                                    placeholder="Please type your question"
                                    className="input-bar"
                                    onFocus={() => setIsFocused(true)}
                                    onBlur={() => setIsFocused(false)}
                                />
                                <button onClick={updateStrategies} className={`request-hint-button ${isFocused ? 'focused' : ''}`}>&#x25BC;</button>
                            </div>
                        </div>
                    )}
                    {showStrategies && (
                        <div className="strategies-content slide-in">
                            <div className="section-header">
                                <button className="back-button" onClick={handleBackClick}>{'<'}</button>
                                <h3 className="underlined">Strategies</h3>
                            </div>
                            <p>We identify that you are in [stage] stage. Here are three different ways that the AI can help you on [this stage]:</p>
                            {strategyColors.map((color, index) => (
                                <div className="strategy" style={{ backgroundColor: color }} key={index}>
                                    <div className="strategy-header">
                                        <div className="left-header">
                                            <h5 className='context-number' style={{ color: colorMap[color] }}>{index + 1}.</h5>
                                            <h4>Strategy {index + 1}</h4>
                                        </div>
                                        <button className="narrow-right-button" onClick={handleNarrowRightClick}>{'>'}</button>
                                    </div>
                                    <p>Strategy description for strategy {index + 1}.</p>
                                    <ul>
                                        <li><strong>Pros:</strong> Pros of strategy {index + 1}</li>
                                        <li><strong>Cons:</strong> Cons of strategy {index + 1}</li>
                                    </ul>
                                    <p><strong>Preview:</strong> Preview of strategy {index + 1}</p>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
                {showPrompt && (
                    <div className="prompt-section slide-in">
                        <div className="section-header">
                            <button className="back-button" onClick={handleBackClick}>{'<'}</button>
                            <h3 className="prompt-h3">Prompt</h3>
                        </div>
                        <p>Here is the prompt for xxxx. You can edit it directly inside.</p>
                        <div className="prompt-content">
                            <div className='prompt-header'>
                                <p><strong>Instruction for constructing this certain type of output</strong></p>
                                <button className={`toggle-button ${collapsedSections[1] ? 'collapsed' : ''}`} onClick={() => toggleSection(1)}>{collapsedSections[1] ? 'v' : '^'}</button>
                            </div>
                            {!collapsedSections[1] && (
                                <p className="editable-text" contentEditable="true" suppressContentEditableWarning={true}>
                                    You are an experienced programming tutor and I am a student asking you for help with my Python code. Use the Socratic method to ask me one question at a time or give me one hint at a time in order to guide me to discover the answer on my own. Do NOT directly give me the answer. Even if I give up and ask you for the answer, do not give me the answer. Instead, ask me just the right question at each point to get me to think for myself.
                                </p>
                            )}
                        </div>
                        <div className="prompt-content">
                            <div className='prompt-header'>
                                <p><strong>Learner’s Context Information</strong></p>
                                <button className={`toggle-button ${collapsedSections[2] ? 'collapsed' : ''}`} onClick={() => toggleSection(2)}>{collapsedSections[2] ? 'v' : '^'}</button>
                            </div>
                            {!collapsedSections[2] && (
                                <p className="editable-text" contentEditable="true" suppressContentEditableWarning={true}>
                                    Do NOT edit my code or write new code for me since that might give away the answer. Instead, give me hints of where to look in my existing code for where the problem might be. You can also print out specific parts of my code to point me in the right direction.
                                </p>
                            )}
                        </div>
                        <div className="prompt-content">
                            <div className='prompt-header'>
                                <p><strong>Problem’s Context Information</strong></p>
                                <button className={`toggle-button ${collapsedSections[3] ? 'collapsed' : ''}`} onClick={() => toggleSection(3)}>{collapsedSections[3] ? 'v' : '^'}</button>
                            </div>
                            {!collapsedSections[3] && (
                                <p className="editable-text" contentEditable="true" suppressContentEditableWarning={true}>
                                    Do NOT use advanced concepts that students in an introductory class have not learned yet. Instead, use concepts that are taught in introductory-level classes and beginner-level programming tutorials. Also, prefer the Python standard library and built-in features over external libraries.
                                </p>
                            )}
                        </div>
                        <div className="prompt-content">
                            <div className='prompt-header'>
                                <p><strong>Problem’s Context Information</strong></p>
                                <button className={`toggle-button ${collapsedSections[4] ? 'collapsed' : ''}`} onClick={() => toggleSection(4)}>{collapsedSections[4] ? 'v' : '^'}</button>
                            </div>
                            {!collapsedSections[4] && (
                                <p className="editable-text" contentEditable="true" suppressContentEditableWarning={true}>
                                    Here is my Python code, which uses Python 3.6:
                                    <pre>
                                        <code>
                                            {`def listSum(numbers):\n    if not numbers:\n        return 0\n    else:\n        (f, rest) = numbers\n        return f + listSum(rest)`}
                                        </code>
                                    </pre>
                                </p>
                            )}
                        </div>
                        <div className="ask-for-help">
                            <button className="ask-for-help-button" onClick={handleAskForHelpClick}>Ask For Help</button>
                        </div>
                    </div>
                )}
                {showHelp && (
                    <div className="help-section slide-in">
                        <div className="section-header">
                            <button className="back-button" onClick={handleBackClick}>{'<'}</button>
                            <h3 className="help-h3">Help</h3>
                        </div>
                        <p>To help you identify where the issue might be occurring in your code, you can add a print statement to check the values of nums[i] and nums[i+1] during each iteration of the loop. This will allow you to see what sums are being calculated and compare them against the target.</p>
                        <p>Here’s your modified code with the added print statement:</p>
                        <pre>
                            <code>
                                {`def two_sum(nums, target):\n    for i in range(len(nums) - 1):  # Change here to prevent index out of range error\n        print(f"Checking indices {i} and {i+1}: ({nums[i]}, {nums[i+1]}))")  # Added print statement\n        if nums[i] + nums[i+1] == target:\n            return [i, i+1]`}
                            </code>
                        </pre>
                        <p>This modification includes a print statement within the loop that outputs the indices being checked and their corresponding values. Make sure to adjust your loop range to len(nums) - 1 to avoid an 'index out of range' error when accessing nums[i+1].</p>
                        <div className='help-input-section'>
                            {conversation.map((message, index) => (
                                <div key={index}>
                                    <div className="chat-bubble">
                                        <span>{message.user}</span>
                                        <img src={userprofile} alt="User Profile" className="user-profile"/>
                                    </div>
                                    <div className="system-response">
                                        <p>{message.system}</p>
                                    </div>
                                </div>
                            ))}
                            <div className={`input-container ${isFocused ? 'focused' : ''}`}>
                                <input
                                    type="text"
                                    value={helpInput}
                                    onChange={handleHelpInputChange}
                                    onKeyPress={handleHelpKeyPress}
                                    placeholder="Please type your question"
                                    className="input-bar"
                                    onFocus={() => setIsFocused(true)}
                                    onBlur={() => setIsFocused(false)}
                                />
                                <button onClick={displaySystemResponse} className={`request-hint-button ${isFocused ? 'focused' : ''}`}>&#x25BC;</button>
                            </div>
                        </div>
                    </div>
                )}
            </div>
            
            <style jsx>{`
                .hints {
                    border: 1px solid #696868;
                    border-radius: 4px;
                    margin-bottom: 10px;
                    padding: 10px;
                    resize: both;
                    overflow: auto;
                    padding-top: 0px;
                    padding-left: 0px;
                    padding-right: 0px;
                }
                .hints .navbar {
                    overflow: hidden;
                    background-color: transparent;
                    border-bottom: 1px solid #979BA1;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
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
.navbar .reset-button {
                    margin-right: 10px;
                    padding: 2px 4px;
                    cursor: pointer;
                    border: 1px solid #BEC8CA;
                    background-color: white;
                    color: #000;
                    font-weight: lighter;
                    border-radius: 4px;
                }
                .navbar .reset-button:hover {
                color:#000;
                    border: 1px solid black;
                    text-decoration: none;

                }
                .content {
                    padding: 20px;
                }
                .input-container {
                    display: flex;
                    align-items: center;
                    border: 1px solid #ccc;
                    margin: 10px 0;
                    border-radius: 8px;
                    flex-grow: 1;
                    transition: background-color 0.3s, color 0.3s;
                }
                .input-bar {
                    width: 80%;
                    background-color: transparent;
                    padding: 10px;
                    border: none;
                    outline: none;
                    flex-grow: 1;
                }
                .request-hint-button {
                    padding: 10px;
                    border: none;
                    background-color: transparent;
                    color: #757778;
                    cursor: pointer;
                    transform: rotate(-90deg);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    transition: background-color 0.3s, color 0.3s;
                }
                .request-hint-button:hover {
                    color: black;
                }
                .input-container.focused {
                    border: 1px solid black;  
                }
                .request-hint-button.focused {
                    color: black;
                }
                .strategies-content {
                    margin-top: 20px;
                    animation: slide-in 0.5s ease-in;
                }
                .context-number {
                    font-size: 1.25rem;
                    font-weight: 400;
                    margin: 1em 0 .8em 0;
                }
               

                h4 {
                    font-weight: 400;
                    font-size: 1.25rem;
                    margin: 1em 0 .8em 0;
                }
                .strategy {
                    margin-top: 10px;
                    padding: 12px;
                    border-radius: 8px;
                }
                .strategy-header {
                    display: flex;
                    align-items: center;
                    justify-content: space-between; /* Keep this */
                    height: 32px;
                    line-height: 1.2;
                }
                .left-header {
                    display: flex;
                    align-items: center;
                }
                .left-header .context-number {
                    margin-right: 10px;
                }
                .narrow-right-button {
                    background: none;
                    border: none;
                    font-size: 16px;
                    cursor: pointer;
                    color: #696868;
                }
                .narrow-right-button:hover {
                    color: black;
                }
                .section-header {
              
                    display: flex;
                    align-items: center;
                 
                }
                
                .back-button {
                    background: none;
                    border: none;
                    font-size: 16px;
                    cursor: pointer;
                    color: #696868;
                    margin-right: 1rem;
                    margin-bottom: 1rem;
                }
                .back-button:hover {
                    color: black;
                }
                .prompt-section {
                    margin-top: 20px;
                    padding: 10px;
                    border-radius: 8px;
                }
                .prompt-content {
                    margin-bottom: 20px;
                    border-bottom: 1px solid #C1C3C6;
                }
                     .prompt-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }
                .toggle-button {
                    background: none;
                    border: none;
                    font-size: 16px;
                    cursor: pointer;
                    color: #696868;
                }
                .editable-text {
                    background-color: #f3f4f4; 
                    border-radius: 4px;
                    padding: 10px;
                    

                }
                .ask-for-help {
    display: flex;
    justify-content: flex-end; 
    margin-top: 10px;
}
                .ask-for-help-button {

                    padding: 10px 20px;
                    background-color: #FFFFFF;
                    border: 1px solid #696868;
                    color: black;
                    font-weight: 400;
                    border-radius: 4px;
                    cursor: pointer;
            
                }
                .ask-for-help-button:hover {
                    border: 1px solid black;
                }
                .help-input-section {
                    margin-top: 20px;
                }
                .chat-bubble {
                    display: flex;
                    align-items: center;
                    justify-content: flex-end;
                    margin-bottom: 10px;
                }
                .chat-bubble span {
                    background-color: #ffffff;
                    border: 1px solid #C1C3C6;
                    border-radius: 15px;
                    padding: 10px 15px;
                    margin-right: 10px;
                    max-width: 60%;
                }
                .user-profile {
                    width: 30px;
                    height: 30px;
                    border-radius: 50%;
                }
                .system-response {
                    margin-top: 10px;
                    margin-bottom: 10px;
                    background-color: #F3F4F4;
                    border-radius: 10px;
                    padding: 10px;
                }
         
                @keyframes slide-in {
                    from {
                        transform: translateY(100%);
                        opacity: 0;
                    }
                    to {
                        transform: translateY(0);
                        opacity: 1;
                    }
                }
            `}</style>
        </div>
    );
};

export default Hints;
