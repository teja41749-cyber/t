import React, { useState } from 'react';
import styled from 'styled-components';
import RequirementInput from './components/RequirementInput';
import DiagramViewer from './components/DiagramViewer';
import ChatInterface from './components/ChatInterface';
import ExportButtons from './components/ExportButtons';
import Header from './components/Header';
import { useNLP } from './hooks/useNLP';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

const AppContainer = styled.div`
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  flex-direction: column;
`;

const MainContent = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: var(--spacing-lg);
  gap: var(--spacing-lg);
`;

const WorkflowContainer = styled.div`
  background: var(--bg-primary);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  padding: var(--spacing-lg);
  min-height: 500px;
`;

const WorkflowContent = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-lg);
  height: 100%;
`;

const LeftPanel = styled.div`
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
`;

const RightPanel = styled.div`
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
  border-left: 1px solid var(--border-color);
  padding-left: var(--spacing-lg);
`;

const EmptyState = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 400px;
  text-align: center;
  color: var(--text-muted);

  h3 {
    margin-bottom: var(--spacing-md);
    color: var(--text-secondary);
  }

  p {
    max-width: 400px;
    line-height: 1.6;
  }
`;

const LoadingOverlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
`;

const LoadingContent = styled.div`
  background: var(--bg-primary);
  padding: var(--spacing-xl);
  border-radius: var(--radius-lg);
  text-align: center;
  box-shadow: var(--shadow-lg);

  .spinner {
    margin: 0 auto var(--spacing-md);
  }
`;

function App() {
  const [currentStep, setCurrentStep] = useState('input'); // input, processing, diagram, chat
  const [umlModel, setUmlModel] = useState(null);
  const [mermaidCode, setMermaidCode] = useState('');
  const [showChat, setShowChat] = useState(false);

  const {
    extractUML,
    isLoading: isNLPProcessing,
    error: nlpError,
    clearError
  } = useNLP();

  const handleRequirementsSubmit = async (text) => {
    try {
      setCurrentStep('processing');
      clearError();

      const result = await extractUML(text);

      if (result) {
        setUmlModel(result.uml_model);
        setMermaidCode(result.mermaid_code);
        setCurrentStep('diagram');
        setShowChat(true);

        toast.success('UML diagram generated successfully! You can now chat with me to refine it.');
      }
    } catch (error) {
      console.error('Error processing requirements:', error);
      setCurrentStep('input');
      toast.error('Failed to generate UML diagram. Please try again.');
    }
  };

  const handleRegenerate = () => {
    setCurrentStep('input');
    setUmlModel(null);
    setMermaidCode('');
    setShowChat(false);
    clearError();
  };

  const handleDiagramUpdate = (updatedModel, updatedCode) => {
    setUmlModel(updatedModel);
    setMermaidCode(updatedCode);
  };

  const renderContent = () => {
    switch (currentStep) {
      case 'input':
        return (
          <WorkflowContainer>
            <RequirementInput
              onSubmit={handleRequirementsSubmit}
              isLoading={isNLPProcessing}
            />
            <EmptyState>
              <h3>🏗️ Welcome to UML Class Diagram Generator</h3>
              <p>
                Paste your software requirements above, and I'll use AI to automatically extract
                classes, attributes, and relationships to create a UML class diagram.
                Then we can refine it together through conversation!
              </p>
            </EmptyState>
          </WorkflowContainer>
        );

      case 'processing':
        return (
          <WorkflowContainer>
            <EmptyState>
              <div className="spinner"></div>
              <h3>🤖 Analyzing Your Requirements</h3>
              <p>
                I'm using advanced NLP models to understand your requirements and extract
                the UML structure. This may take a few moments...
              </p>
            </EmptyState>
          </WorkflowContainer>
        );

      case 'diagram':
      case 'chat':
        return (
          <WorkflowContainer>
            <WorkflowContent>
              <LeftPanel>
                <DiagramViewer
                  mermaidCode={mermaidCode}
                  umlModel={umlModel}
                  onDiagramUpdate={handleDiagramUpdate}
                />
                <ExportButtons
                  umlModel={umlModel}
                  mermaidCode={mermaidCode}
                />
              </LeftPanel>
              <RightPanel>
                <ChatInterface
                  umlModel={umlModel}
                  onDiagramUpdate={handleDiagramUpdate}
                  isVisible={showChat}
                />
              </RightPanel>
            </WorkflowContent>
          </WorkflowContainer>
        );

      default:
        return null;
    }
  };

  return (
    <AppContainer>
      <Header
        currentStep={currentStep}
        onRegenerate={currentStep !== 'input' ? handleRegenerate : null}
      />

      <MainContent>
        {renderContent()}
      </MainContent>

      {isNLPProcessing && (
        <LoadingOverlay>
          <LoadingContent>
            <div className="spinner"></div>
            <h3>Processing Your Requirements</h3>
            <p>Using AI to extract UML elements...</p>
          </LoadingContent>
        </LoadingOverlay>
      )}

      <ToastContainer
        position="bottom-right"
        autoClose={5000}
        hideProgressBar={false}
        newestOnTop={false}
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
      />
    </AppContainer>
  );
}

export default App;