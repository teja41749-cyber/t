import React, { useState, useEffect, useRef } from 'react';
import styled from 'styled-components';
import { chatAPI } from '../services/api';

const ChatContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 500px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  background: var(--bg-primary);
`;

const ChatHeader = styled.div`
  padding: var(--spacing-md);
  border-bottom: 1px solid var(--border-color);
  background: var(--gray-50);
  border-radius: var(--radius-md) var(--radius-md) 0 0;
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
`;

const ChatTitle = styled.h3`
  margin: 0;
  font-size: var(--text-base);
  color: var(--text-primary);
`;

const ChatStatus = styled.div`
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  font-size: var(--text-xs);
  color: ${props => props.online ? 'var(--success-color)' : 'var(--text-muted)'};
  margin-left: auto;
`;

const StatusDot = styled.div`
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: ${props => props.online ? 'var(--success-color)' : 'var(--gray-400)'};
`;

const ChatMessages = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: var(--spacing-md);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
`;

const Message = styled.div`
  display: flex;
  gap: var(--spacing-sm);
  max-width: 80%;
  ${props => props.isUser ? 'align-self: flex-end;' : 'align-self: flex-start;'}
`;

const MessageAvatar = styled.div`
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--text-sm);
  flex-shrink: 0;
  ${props => props.isUser ?
    'background: var(--primary-color); color: white;' :
    'background: var(--gray-100); color: var(--text-secondary);'}
`;

const MessageContent = styled.div`
  background: ${props => props.isUser ?
    'var(--primary-color); color: white;' :
    'var(--gray-100); color: var(--text-primary);'};
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--radius-md);
  border-bottom-left-radius: ${props => props.isUser ? 'var(--radius-md)' : '4px'};
  border-bottom-right-radius: ${props => props.isUser ? '4px' : 'var(--radius-md)'};
  box-shadow: var(--shadow-sm);
`;

const MessageText = styled.div`
  font-size: var(--text-sm);
  line-height: 1.4;
  white-space: pre-wrap;
  word-wrap: break-word;
`;

const MessageTime = styled.div`
  font-size: var(--text-xs);
  color: ${props => props.isUser ?
    'rgba(255, 255, 255, 0.7);' :
    'var(--text-muted);'};
  margin-top: var(--spacing-xs);
`;

const QuickReplies = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-xs);
  margin-top: var(--spacing-sm);
`;

const QuickReplyButton = styled.button`
  padding: var(--spacing-xs) var(--spacing-sm);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  background: var(--bg-primary);
  color: var(--text-secondary);
  font-size: var(--text-xs);
  cursor: pointer;
  transition: all var(--transition);

  &:hover {
    background: var(--primary-color);
    border-color: var(--primary-color);
    color: white;
  }
`;

const ChatInput = styled.div`
  padding: var(--spacing-md);
  border-top: 1px solid var(--border-color);
  display: flex;
  gap: var(--spacing-sm);
`;

const InputField = styled.input`
  flex: 1;
  padding: var(--spacing-sm) var(--spacing-md);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  font-size: var(--text-sm);
  transition: border-color var(--transition);

  &:focus {
    outline: none;
    border-color: var(--border-focus);
    box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.1);
  }
`;

const SendButton = styled.button`
  padding: var(--spacing-sm) var(--spacing-md);
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: var(--radius);
  font-size: var(--text-sm);
  cursor: pointer;
  transition: background-color var(--transition);
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);

  &:hover:not(:disabled) {
    background: var(--primary-hover);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const TypingIndicator = styled.div`
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-md);
  background: var(--gray-100);
  border-radius: var(--radius-md);
  margin-bottom: var(--spacing-sm);
  align-self: flex-start;
`;

const TypingDot = styled.div`
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--text-muted);
  animation: typing 1.4s infinite ease-in-out;

  &:nth-child(1) { animation-delay: -0.32s; }
  &:nth-child(2) { animation-delay: -0.16s; }

  @keyframes typing {
    0%, 80%, 100% {
      transform: scale(0.8);
      opacity: 0.5;
    }
    40% {
      transform: scale(1);
      opacity: 1;
    }
  }
`;

const ChatInterface = ({ umlModel, onDiagramUpdate, isVisible }) => {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isOnline, setIsOnline] = useState(false);
  const [quickReplies, setQuickReplies] = useState([]);
  const messagesEndRef = useRef(null);
  const senderId = `user-${Date.now()}`;

  // Initialize chat when diagram is available
  useEffect(() => {
    if (umlModel && isVisible && messages.length === 0) {
      initializeChat();
    }
  }, [umlModel, isVisible]);

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Check chat service availability
  useEffect(() => {
    checkChatStatus();
    const interval = setInterval(checkChatStatus, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const initializeChat = () => {
    const welcomeMessage = {
      id: 'welcome',
      text: `Hello! I'm your UML diagram assistant. I've analyzed your requirements and extracted a diagram with ${umlModel?.classes?.length || 0} classes and ${umlModel?.relationships?.length || 0} relationships.

I can help you:
- Validate relationships between classes
- Add or remove classes, attributes, and methods
- Change relationship types (composition, association, etc.)
- Export your diagram

What would you like to do with your diagram?`,
      isUser: false,
      timestamp: new Date(),
      quickReplies: [
        'Validate relationships',
        'Add a class',
        'Export diagram',
        'Show statistics'
      ]
    };

    setMessages([welcomeMessage]);
    setQuickReplies(welcomeMessage.quickReplies);
  };

  const checkChatStatus = async () => {
    try {
      // Simple check - try to connect to Rasa server
      await chatAPI.sendMessage('/ping', senderId);
      setIsOnline(true);
    } catch (error) {
      setIsOnline(false);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const sendMessage = async (text) => {
    if (!text.trim()) return;

    const userMessage = {
      id: `user-${Date.now()}`,
      text: text.trim(),
      isUser: true,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setQuickReplies([]);
    setIsTyping(true);

    try {
      const response = await chatAPI.sendMessage(text, senderId);

      if (response && response.length > 0) {
        const botMessages = response.map((msg, index) => ({
          id: `bot-${Date.now()}-${index}`,
          text: msg.text,
          isUser: false,
          timestamp: new Date(),
          quickReplies: msg.buttons ? msg.buttons.map(btn => btn.title) : []
        }));

        setMessages(prev => [...prev, ...botMessages]);

        // Set quick replies from last message
        const lastMessage = botMessages[botMessages.length - 1];
        if (lastMessage.quickReplies.length > 0) {
          setQuickReplies(lastMessage.quickReplies);
        }
      } else {
        // Fallback response if chat service is unavailable
        const fallbackMessage = {
          id: `fallback-${Date.now()}`,
          text: `I understand you want to "${text}".

Since the chat service is currently unavailable, you can use the diagram controls above to manually export your diagram or make changes. I apologize for the inconvenience!`,
          isUser: false,
          timestamp: new Date()
        };

        setMessages(prev => [...prev, fallbackMessage]);
      }
    } catch (error) {
      console.error('Chat error:', error);

      const errorMessage = {
        id: `error-${Date.now()}`,
        text: 'Sorry, I\'m having trouble connecting right now. You can still use the export buttons to save your diagram, or try refreshing the page.',
        isUser: false,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleQuickReply = (reply) => {
    sendMessage(reply);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage(inputText);
    }
  };

  const formatTime = (date) => {
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (!isVisible) {
    return null;
  }

  return (
    <ChatContainer>
      <ChatHeader>
        <ChatTitle>💬 Diagram Assistant</ChatTitle>
        <ChatStatus online={isOnline}>
          <StatusDot online={isOnline} />
          {isOnline ? 'Online' : 'Offline'}
        </ChatStatus>
      </ChatHeader>

      <ChatMessages>
        {messages.map((message) => (
          <Message key={message.id} isUser={message.isUser}>
            <MessageAvatar isUser={message.isUser}>
              {message.isUser ? '👤' : '🤖'}
            </MessageAvatar>
            <div>
              <MessageContent isUser={message.isUser}>
                <MessageText>{message.text}</MessageText>
                <MessageTime isUser={message.isUser}>
                  {formatTime(message.timestamp)}
                </MessageTime>
              </MessageContent>
              {message.quickReplies && (
                <QuickReplies>
                  {message.quickReplies.map((reply, index) => (
                    <QuickReplyButton
                      key={index}
                      onClick={() => handleQuickReply(reply)}
                    >
                      {reply}
                    </QuickReplyButton>
                  ))}
                </QuickReplies>
              )}
            </div>
          </Message>
        ))}

        {isTyping && (
          <TypingIndicator>
            <MessageAvatar isUser={false}>🤖</MessageAvatar>
            <div>
              <MessageContent isUser={false}>
                <TypingDot />
                <TypingDot />
                <TypingDot />
              </MessageContent>
            </div>
          </TypingIndicator>
        )}

        <div ref={messagesEndRef} />
      </ChatMessages>

      <ChatInput>
        <InputField
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask me about your diagram..."
          disabled={isTyping}
        />
        <SendButton
          onClick={() => sendMessage(inputText)}
          disabled={!inputText.trim() || isTyping}
        >
          Send ➤
        </SendButton>
      </ChatInput>
    </ChatContainer>
  );
};

export default ChatInterface;