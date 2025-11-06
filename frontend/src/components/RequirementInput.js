import React, { useState, useEffect } from 'react';
import styled from 'styled-components';

const InputContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
`;

const TextArea = styled.textarea`
  width: 100%;
  min-height: 200px;
  padding: var(--spacing-md);
  border: 2px solid var(--border-color);
  border-radius: var(--radius-md);
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: var(--text-sm);
  line-height: 1.6;
  resize: vertical;
  transition: border-color var(--transition);

  &:focus {
    outline: none;
    border-color: var(--border-focus);
    box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.1);
  }

  &.error {
    border-color: var(--border-error);
  }

  &::placeholder {
    color: var(--text-muted);
    font-style: italic;
  }
`;

const InputFooter = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--spacing-md);
`;

const CharacterCount = styled.div`
  font-size: var(--text-xs);
  color: ${props => {
    if (props.count < 50) return var(--danger-color);
    if (props.count > 10000) return var(--danger-color);
    return var(--text-muted);
  }};
`;

const ValidationMessage = styled.div`
  font-size: var(--text-sm);
  color: ${props => props.type === 'error' ? var(--danger-color) :
                    props.type === 'warning' ? var(--warning-color) :
                    var(--success-color)};
  margin-top: var(--spacing-xs);
`;

const SampleButtons = styled.div`
  display: flex;
  gap: var(--spacing-sm);
  flex-wrap: wrap;
`;

const SampleButton = styled.button`
  padding: var(--spacing-xs) var(--spacing-sm);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  background: var(--bg-primary);
  color: var(--text-secondary);
  font-size: var(--text-xs);
  cursor: pointer;
  transition: all var(--transition);

  &:hover {
    background: var(--gray-50);
    border-color: var(--primary-color);
    color: var(--primary-color);
  }
`;

const HelpText = styled.div`
  background: var(--gray-50);
  padding: var(--spacing-md);
  border-radius: var(--radius);
  border-left: 4px solid var(--primary-color);
  font-size: var(--text-sm);
  color: var(--text-secondary);
  margin-bottom: var(--spacing-md);
`;

const samples = {
  ecommerce: `Users can create accounts with username and password. Users have shopping carts that contain multiple products. Products have prices and descriptions. Orders are created from carts and contain order details. Users can add items to their cart and checkout to complete purchases.`,

  education: `Students enroll in courses. Courses have instructors. Students submit assignments. Instructors grade assignments and provide feedback. Courses have schedules and prerequisites. Students can view their grades and academic progress.`,

  banking: `Customers have bank accounts with account numbers and balances. Accounts can be checking or savings. Customers can transfer money between accounts. Transactions are recorded with timestamps and amounts. Bank employees can manage customer accounts and authorize large transactions.`,

  library: `Library members can borrow books. Books have titles, authors, and ISBN numbers. Members have membership cards with expiry dates. The library tracks due dates and late fees. Librarians can add new books and manage the catalog.`
};

const RequirementInput = ({ onSubmit, isLoading }) => {
  const [text, setText] = useState('');
  const [validation, setValidation] = useState({ isValid: true, message: '', type: 'info' });

  useEffect(() => {
    validateInput(text);
  }, [text]);

  // Load saved text from localStorage
  useEffect(() => {
    const savedText = localStorage.getItem('uml-requirements-text');
    if (savedText) {
      setText(savedText);
    }
  }, []);

  // Save text to localStorage
  useEffect(() => {
    if (text) {
      localStorage.setItem('uml-requirements-text', text);
    }
  }, [text]);

  const validateInput = (inputText) => {
    const length = inputText.trim().length;

    if (length === 0) {
      setValidation({
        isValid: true,
        message: '',
        type: 'info'
      });
      return;
    }

    if (length < 50) {
      setValidation({
        isValid: false,
        message: `Text is too short (${length}/50 characters). Please provide more detailed requirements.`,
        type: 'error'
      });
      return;
    }

    if (length > 10000) {
      setValidation({
        isValid: false,
        message: `Text is too long (${length}/10000 characters). Please shorten your requirements.`,
        type: 'error'
      });
      return;
    }

    // Check for meaningful content
    const meaningfulIndicators = ['class', 'user', 'system', 'has', 'contains', 'manages', 'interface', 'data'];
    const hasMeaningfulContent = meaningfulIndicators.some(indicator =>
      inputText.toLowerCase().includes(indicator)
    );

    if (!hasMeaningfulContent) {
      setValidation({
        isValid: true,
        message: 'Your text might not contain sufficient software requirements. Consider adding more specific details about classes, relationships, or system components.',
        type: 'warning'
      });
    } else {
      setValidation({
        isValid: true,
        message: 'Requirements look good! Ready to generate your UML diagram.',
        type: 'success'
      });
    }
  };

  const handleSubmit = () => {
    if (validation.isValid && text.trim().length >= 50) {
      onSubmit(text.trim());
      // Clear localStorage after successful submission
      localStorage.removeItem('uml-requirements-text');
    }
  };

  const handleSampleClick = (sampleKey) => {
    setText(samples[sampleKey]);
  };

  const characterCount = text.length;
  const isValidLength = characterCount >= 50 && characterCount <= 10000;
  const canSubmit = validation.isValid && isValidLength && !isLoading;

  return (
    <InputContainer>
      <HelpText>
        <strong>💡 Tip:</strong> Describe your software system requirements. Include classes, their attributes, relationships, and behaviors. The more detailed your description, the better the generated UML diagram will be.
      </HelpText>

      <TextArea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Enter your software requirements here...

Example: A user management system where users can create accounts with username and password. Users have profiles with personal information. Administrators can manage user accounts and view system statistics. The system tracks user login history and permissions..."
        className={!validation.isValid ? 'error' : ''}
        disabled={isLoading}
      />

      <InputFooter>
        <CharacterCount count={characterCount}>
          {characterCount} characters {characterCount < 50 && `(minimum 50)`}
          {characterCount > 10000 && `(maximum 10000)`}
        </CharacterCount>

        <button
          className={`btn btn-primary ${canSubmit ? '' : 'disabled'}`}
          onClick={handleSubmit}
          disabled={!canSubmit}
        >
          {isLoading ? (
            <>
              <div className="spinner" style={{ width: '16px', height: '16px', marginRight: '8px' }} />
              Processing...
            </>
          ) : (
            '🚀 Generate UML Diagram'
          )}
        </button>
      </InputFooter>

      {validation.message && (
        <ValidationMessage type={validation.type}>
          {validation.message}
        </ValidationMessage>
      )}

      <SampleButtons>
        <span style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)', marginRight: 'var(--spacing-sm)' }}>
          Try examples:
        </span>
        <SampleButton onClick={() => handleSampleClick('ecommerce')}>
          E-commerce
        </SampleButton>
        <SampleButton onClick={() => handleSampleClick('education')}>
          Education System
        </SampleButton>
        <SampleButton onClick={() => handleSampleClick('banking')}>
          Banking System
        </SampleButton>
        <SampleButton onClick={() => handleSampleClick('library')}>
          Library System
        </SampleButton>
      </SampleButtons>
    </InputContainer>
  );
};

export default RequirementInput;