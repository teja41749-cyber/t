import React, { useState } from 'react';
import styled from 'styled-components';
import { diagramAPI, downloadFile } from '../services/api';

const ExportContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
`;

const ExportTitle = styled.h4`
  margin: 0;
  font-size: var(--text-base);
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
`;

const ExportButtonContainer = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-sm);
`;

const ExportButton = styled.button`
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  padding: var(--spacing-sm) var(--spacing-md);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  background: var(--bg-primary);
  color: var(--text-secondary);
  font-size: var(--text-sm);
  cursor: pointer;
  transition: all var(--transition);
  position: relative;

  &:hover:not(:disabled) {
    background: var(--gray-50);
    border-color: var(--primary-color);
    color: var(--primary-color);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const ExportStatus = styled.div`
  font-size: var(--text-xs);
  color: ${props => {
    switch (props.type) {
      case 'success': return 'var(--success-color)';
      case 'error': return 'var(--danger-color)';
      case 'warning': return 'var(--warning-color)';
      default: return 'var(--text-muted)';
    }
  }};
  margin-top: var(--spacing-xs);
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
`;

const ExportButtons = ({ umlModel, mermaidCode }) => {
  const [exportStatus, setExportStatus] = useState({});
  const [isExporting, setIsExporting] = useState({});

  const updateStatus = (format, type, message) => {
    setExportStatus(prev => ({
      ...prev,
      [format]: { type, message }
    }));

    // Clear status after 3 seconds
    setTimeout(() => {
      setExportStatus(prev => {
        const newStatus = { ...prev };
        delete newStatus[format];
        return newStatus;
      });
    }, 3000);
  };

  const handleExport = async (format) => {
    if (!umlModel) {
      updateStatus(format, 'error', 'No diagram to export');
      return;
    }

    setIsExporting(prev => ({ ...prev, [format]: true }));

    try {
      switch (format) {
        case 'mermaid':
          exportMermaid();
          break;
        case 'json':
          await exportJSON();
          break;
        case 'svg':
          await exportSVG();
          break;
        case 'png':
          await exportPNG();
          break;
        default:
          updateStatus(format, 'error', 'Unsupported format');
      }
    } catch (error) {
      console.error(`Export ${format} error:`, error);
      updateStatus(format, 'error', `Export failed: ${error.message}`);
    } finally {
      setIsExporting(prev => ({ ...prev, [format]: false }));
    }
  };

  const exportMermaid = () => {
    if (!mermaidCode) {
      updateStatus('mermaid', 'error', 'No Mermaid code available');
      return;
    }

    try {
      downloadFile(mermaidCode, 'uml-diagram.mmd', 'text/plain');
      updateStatus('mermaid', 'success', 'Mermaid file downloaded');
    } catch (error) {
      updateStatus('mermaid', 'error', 'Failed to download Mermaid file');
    }
  };

  const exportJSON = async () => {
    try {
      const response = await diagramAPI.exportDiagram(umlModel, 'json');
      downloadFile(response.data, response.filename, 'application/json');
      updateStatus('json', 'success', 'JSON file downloaded');
    } catch (error) {
      updateStatus('json', 'error', `JSON export failed: ${error.message}`);
    }
  };

  const exportSVG = async () => {
    try {
      // Get the SVG from the current diagram viewer
      const svgElement = document.querySelector('.mermaid svg');
      if (svgElement) {
        const svgData = new XMLSerializer().serializeToString(svgElement);
        const blob = new Blob([svgData], { type: 'image/svg+xml' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'uml-diagram.svg';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        updateStatus('svg', 'success', 'SVG image downloaded');
      } else {
        updateStatus('svg', 'error', 'No diagram found to export');
      }
    } catch (error) {
      updateStatus('svg', 'error', 'SVG export failed');
    }
  };

  const exportPNG = async () => {
    try {
      const svgElement = document.querySelector('.mermaid svg');
      if (svgElement) {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        const svgData = new XMLSerializer().serializeToString(svgElement);
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
        updateStatus('png', 'success', 'PNG image downloaded');
      } else {
        updateStatus('png', 'error', 'No diagram found to export');
      }
    } catch (error) {
      updateStatus('png', 'error', 'PNG export failed');
    }
  };

  const copyToClipboard = async (format) => {
    try {
      let content = '';

      switch (format) {
        case 'mermaid':
          content = mermaidCode;
          break;
        case 'json':
          content = JSON.stringify(umlModel, null, 2);
          break;
        default:
          updateStatus(format, 'error', 'Cannot copy this format');
          return;
      }

      await navigator.clipboard.writeText(content);
      updateStatus(format, 'success', 'Copied to clipboard');
    } catch (error) {
      updateStatus(format, 'error', 'Failed to copy to clipboard');
    }
  };

  const exportFormats = [
    {
      key: 'mermaid',
      label: 'Mermaid',
      icon: '📄',
      description: 'Mermaid diagram code',
      hasCopy: true
    },
    {
      key: 'json',
      label: 'JSON',
      icon: '🔧',
      description: 'UML model data',
      hasCopy: true
    },
    {
      key: 'svg',
      label: 'SVG',
      icon: '🖼️',
      description: 'Vector image',
      hasCopy: false
    },
    {
      key: 'png',
      label: 'PNG',
      icon: '📷',
      description: 'Raster image',
      hasCopy: false
    }
  ];

  return (
    <ExportContainer>
      <ExportTitle>
        💾 Export Options
      </ExportTitle>

      <ExportButtonContainer>
        {exportFormats.map((format) => (
          <div key={format.key} style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <div style={{ display: 'flex', gap: '4px' }}>
              <ExportButton
                onClick={() => handleExport(format.key)}
                disabled={!umlModel || isExporting[format.key]}
                title={format.description}
              >
                {isExporting[format.key] ? (
                  <div className="spinner" style={{ width: '12px', height: '12px' }} />
                ) : (
                  format.icon
                )}
                {format.label}
              </ExportButton>

              {format.hasCopy && (
                <ExportButton
                  onClick={() => copyToClipboard(format.key)}
                  disabled={!umlModel}
                  title={`Copy ${format.label} to clipboard`}
                  style={{ padding: 'var(--spacing-sm)' }}
                >
                  📋
                </ExportButton>
              )}
            </div>

            {exportStatus[format.key] && (
              <ExportStatus type={exportStatus[format.key].type}>
                {exportStatus[format.key].type === 'success' && '✓'}
                {exportStatus[format.key].type === 'error' && '✗'}
                {exportStatus[format.key].type === 'warning' && '⚠'}
                {exportStatus[format.key].message}
              </ExportStatus>
            )}
          </div>
        ))}
      </ExportButtonContainer>

      <div style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)', marginTop: 'var(--spacing-sm)' }}>
        <strong>Tip:</strong> Mermaid code can be used in documentation tools like GitHub, GitLab, or Notion.
      </div>
    </ExportContainer>
  );
};

export default ExportButtons;