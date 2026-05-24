import React from 'react';
import Editor from '@monaco-editor/react';
import type { Monaco } from '@monaco-editor/react';

interface CodeEditorProps {
  code: string;
  onChange: (value: string) => void;
  highlightedLine?: number;
}

export const CodeEditor: React.FC<CodeEditorProps> = ({ code, onChange }) => {
  const handleEditorMount = (_editor: any, monaco: Monaco) => {
    // Configure Python syntax
    monaco.languages.register({ id: 'python' });
  };

  return (
    <div className="code-editor">
      <Editor
        height="100%"
        defaultLanguage="python"
        value={code}
        onChange={(value) => onChange(value || '')}
        theme="vs-dark"
        onMount={handleEditorMount}
        options={{
          minimap: { enabled: false },
          fontSize: 14,
          lineNumbers: 'on',
          scrollBeyondLastLine: false,
          automaticLayout: true,
        }}
      />
    </div>
  );
};
