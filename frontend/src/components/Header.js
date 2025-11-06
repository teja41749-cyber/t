import React from 'react';
import styled from 'styled-components';

const HeaderContainer = styled.header`
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  padding: var(--spacing-md) var(--spacing-lg);
  box-shadow: var(--shadow);
  border-bottom: 1px solid var(--border-color);
`;

const HeaderContent = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const Logo = styled.div`
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--text-primary);
`;

const LogoIcon = styled.div`
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: var(--radius);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
`;

const StepsIndicator = styled.div`
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
`;

const Step = styled.div`
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  color: ${props => props.active ? var(--primary-color) : var(--text-muted)};
  font-weight: ${props => props.active ? '600' : '400'};
  font-size: var(--text-sm);
`;

const StepNumber = styled.div`
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: ${props => props.active ? var(--primary-color) : var(--gray-200)};
  color: ${props => props.active ? 'white' : var(--text-muted)};
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--text-xs);
  font-weight: 600;
`;

const StepSeparator = styled.div`
  width: 20px;
  height: 2px;
  background: var(--gray-300);
`;

const Actions = styled.div`
  display: flex;
  gap: var(--spacing-sm);
`;

const Header = ({ currentStep, onRegenerate }) => {
  const getStepStatus = (step) => {
    const stepOrder = ['input', 'processing', 'diagram', 'chat'];
    const currentIndex = stepOrder.indexOf(currentStep);
    const stepIndex = stepOrder.indexOf(step);

    if (stepIndex <= currentIndex) return 'active';
    return 'inactive';
  };

  const steps = [
    { key: 'input', label: 'Input Requirements', icon: '📝' },
    { key: 'processing', label: 'Processing', icon: '🤖' },
    { key: 'diagram', label: 'Review Diagram', icon: '📊' },
    { key: 'chat', label: 'Refine & Chat', icon: '💬' }
  ];

  return (
    <HeaderContainer>
      <HeaderContent>
        <Logo>
          <LogoIcon>UML</LogoIcon>
          <span>AI Diagram Generator</span>
        </Logo>

        <StepsIndicator>
          {steps.map((step, index) => (
            <React.Fragment key={step.key}>
              <Step active={getStepStatus(step.key) === 'active'}>
                <StepNumber active={getStepStatus(step.key) === 'active'}>
                  {index + 1}
                </StepNumber>
                <span>{step.label}</span>
              </Step>
              {index < steps.length - 1 && <StepSeparator />}
            </React.Fragment>
          ))}
        </StepsIndicator>

        <Actions>
          {onRegenerate && (
            <button
              className="btn btn-outline btn-sm"
              onClick={onRegenerate}
            >
              🔄 Start Over
            </button>
          )}
        </Actions>
      </HeaderContent>
    </HeaderContainer>
  );
};

export default Header;