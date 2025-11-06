import React, { useState, useEffect, useRef } from 'react';
import styled from 'styled-components';
import mermaid from 'mermaid';

const ViewerContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
  height: 100%;
  min-height: 400px;
`;

const ViewerHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: var(--spacing-sm);
  border-bottom: 1px solid var(--border-color);
`;

const ViewerTitle = styled.h3`
  margin: 0;
  font-size: var(--text-lg);
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
`;

const ViewerControls = styled.div`
  display: flex;
  gap: var(--spacing-sm);
`;

const ControlButton = styled.button`
  padding: var(--spacing-xs) var(--spacing-sm);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  background: var(--bg-primary);
  color: var(--text-secondary);
  font-size: var(--text-xs);
  cursor: pointer;
  transition: all var(--transition);
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);

  &:hover {
    background: var(--gray-50);
    border-color: var(--primary-color);
    color: var(--primary-color);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const DiagramContent = styled.div`
  flex: 1;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  background: var(--bg-primary);
  position: relative;
  overflow: auto;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 350px;
`;

const DiagramSVG = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  padding: var(--spacing-lg);

  .mermaid {
    display: flex;
    align-items: center;
    justify-content: center;
    max-width: 100%;
    max-height: 100%;
  }

  svg {
    max-width: 100%;
    max-height: 100%;
    height: auto;
  }
`;

const ErrorMessage = styled.div`
  color: var(--danger-color);
  background: var(--gray-50);
  padding: var(--spacing-md);
  border-radius: var(--radius);
  border: 1px solid var(--danger-color);
  text-align: center;
  margin: var(--spacing-md);
`;

const LoadingState = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: var(--text-muted);
`;

const ZoomControls = styled.div`
  position: absolute;
  bottom: var(--spacing-md);
  right: var(--spacing-md);
  display: flex;
  gap: var(--spacing-xs);
  background: rgba(255, 255, 255, 0.9);
  padding: var(--spacing-xs);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
`;

const ZoomButton = styled.button`
  width: 32px;
  height: 32px;
  border: 1px solid var(--border-color);
  background: var(--bg-primary);
  border-radius: var(--radius-sm);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--text-sm);
  transition: all var(--transition);

  &:hover {
    background: var(--gray-50);
    border-color: var(--primary-color);
  }
`;

const DiagramViewer = ({ mermaidCode, umlModel, onDiagramUpdate }) => {
  const [zoom, setZoom] = useState(1);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [diagramId] = useState(`diagram-${Date.now()}`);
  const diagramRef = useRef(null);

  // Initialize Mermaid
  useEffect(() => {
    mermaid.initialize({
      startOnLoad: false,
      theme: 'default',
      securityLevel: 'loose',
      fontFamily: 'monospace',
      fontSize: 14,
      flowchart: {
        useMaxWidth: true,
        htmlLabels: true,
        curve: 'basis'
      },
      themeVariables: {
        primaryColor: '#4299e1',
        primaryTextColor: '#2d3748',
        primaryBorderColor: '#2b6cb0',
        lineColor: '#4a5568',
        sectionBkgColor: '#f7fafc',
        altSectionBkgColor: '#edf2f7',
        gridColor: '#e2e8f0',
        secondaryColor: '#48bb78',
        tertiaryColor: '#ed8936'
      }
    });
  }, []);

  // Render diagram when mermaid code changes
  useEffect(() => {
    if (mermaidCode) {
      renderDiagram();
    }
  }, [mermaidCode]);

  const renderDiagram = async () => {
    if (!mermaidCode || !diagramRef.current) return;

    setIsLoading(true);
    setError(null);

    try {
      // Clear previous diagram
      diagramRef.current.innerHTML = '';

      // Generate unique ID for this diagram
      const elementId = `mermaid-${Date.now()}`;

      // Create container element
      const graphDiv = document.createElement('div');
      graphDiv.id = elementId;
      diagramRef.current.appendChild(graphDiv);

      // Render the diagram
      const { svg } = await mermaid.render(elementId, mermaidCode);
      graphDiv.innerHTML = svg;

      // Apply zoom
      applyZoom(zoom);

    } catch (err) {
      console.error('Mermaid rendering error:', err);
      setError('Failed to render diagram. The Mermaid syntax might be invalid.');
    } finally {
      setIsLoading(false);
    }
  };

  const applyZoom = (zoomLevel) => {
    if (diagramRef.current) {
      const svg = diagramRef.current.querySelector('svg');
      if (svg) {
        svg.style.transform = `scale(${zoomLevel})`;
        svg.style.transformOrigin = 'center';
      }
    }
  };

  const handleZoomIn = () => {
    const newZoom = Math.min(zoom + 0.1, 2);
    setZoom(newZoom);
    applyZoom(newZoom);
  };

  const handleZoomOut = () => {
    const newZoom = Math.max(zoom - 0.1, 0.5);
    setZoom(newZoom);
    applyZoom(newZoom);
  };

  const handleZoomReset = () => {
    setZoom(1);
    applyZoom(1);
  };

  const handleExportSVG = () => {
    if (diagramRef.current) {
      const svg = diagramRef.current.querySelector('svg');
      if (svg) {
        const svgData = new XMLSerializer().serializeToString(svg);
        const blob = new Blob([svgData], { type: 'image/svg+xml' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'uml-diagram.svg';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
      }
    }
  };

  const handleExportPNG = async () => {
    if (diagramRef.current) {
      const svg = diagramRef.current.querySelector('svg');
      if (svg) {
        try {
          const canvas = document.createElement('canvas');
          const ctx = canvas.getContext('2d');
          const svgData = new XMLSerializer().serializeToString(svg);
          const img = new Image();

          img.onload = () => {
            canvas.width = img.width * 2; // Higher resolution
            canvas.height = img.height * 2;
            ctx.scale(2, 2);
            ctx.drawImage(img, 0, 0);

            canvas.toBlob((blob) => {
              const url = URL.createObjectURL(blob);
              const link = document.createElement('a');
              link.href = url;
              link.download = 'uml-diagram.png';
              document.body.appendChild(link);
              link.click();
              document.body.removeChild(link);
              URL.revokeObjectURL(url);
            });
          };

          const svgBlob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' });
          const svgUrl = URL.createObjectURL(svgBlob);
          img.src = svgUrl;
        } catch (err) {
          console.error('PNG export error:', err);
          alert('Failed to export PNG. Try SVG export instead.');
        }
      }
    }
  };

  const getClassCount = () => {
    return umlModel?.classes?.length || 0;
  };

  const getRelationshipCount = () => {
    return umlModel?.relationships?.length || 0;
  };

  return (
    <ViewerContainer>
      <ViewerHeader>
        <ViewerTitle>
          📊 UML Class Diagram
          <span style={{ fontSize: 'var(--text-sm)', color: 'var(--text-muted)', fontWeight: 'normal' }}>
            ({getClassCount()} classes, {getRelationshipCount()} relationships)
          </span>
        </ViewerTitle>
        <ViewerControls>
          <ControlButton onClick={handleExportSVG} disabled={!mermaidCode}>
            📄 Export SVG
          </ControlButton>
          <ControlButton onClick={handleExportPNG} disabled={!mermaidCode}>
            🖼️ Export PNG
          </ControlButton>
          <ControlButton onClick={renderDiagram} disabled={isLoading}>
            🔄 Refresh
          </ControlButton>
        </ViewerControls>
      </ViewerHeader>

      <DiagramContent>
        {isLoading && (
          <LoadingState>
            <div className="spinner"></div>
            <p>Rendering diagram...</p>
          </LoadingState>
        )}

        {error && (
          <ErrorMessage>
            <strong>⚠️ Diagram Error</strong><br />
            {error}
          </ErrorMessage>
        )}

        {!mermaidCode && !isLoading && !error && (
          <LoadingState>
            <p>No diagram to display yet. Generate one by entering requirements above.</p>
          </LoadingState>
        )}

        {mermaidCode && !isLoading && !error && (
          <>
            <DiagramSVG ref={diagramRef} />
            <ZoomControls>
              <ZoomButton onClick={handleZoomOut} title="Zoom Out">
                ➖
              </ZoomButton>
              <ZoomButton onClick={handleZoomReset} title="Reset Zoom">
                🔍
              </ZoomButton>
              <ZoomButton onClick={handleZoomIn} title="Zoom In">
                ➕
              </ZoomButton>
            </ZoomControls>
          </>
        )}
      </DiagramContent>
    </ViewerContainer>
  );
};

export default DiagramViewer;