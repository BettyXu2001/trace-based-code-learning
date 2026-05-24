import React from 'react';

interface VariablePanelProps {
  variables: Record<string, any>;
  prevVariables?: Record<string, any>;
}

export const VariablePanel: React.FC<VariablePanelProps> = ({ variables, prevVariables }) => {
  const entries = Object.entries(variables);

  return (
    <div className="variable-panel">
      <h3>变量状态</h3>
      {entries.length === 0 ? (
        <p className="empty">无变量</p>
      ) : (
        <table className="variable-table">
          <thead>
            <tr>
              <th>变量</th>
              <th>值</th>
              <th>变化</th>
            </tr>
          </thead>
          <tbody>
            {entries.map(([name, value]) => {
              const prevValue = prevVariables?.[name];
              const changed = prevValue !== undefined && prevValue !== value;
              return (
                <tr key={name} className={changed ? 'changed' : ''}>
                  <td className="var-name">{name}</td>
                  <td className="var-value">{JSON.stringify(value)}</td>
                  <td className="var-change">
                    {changed ? `${JSON.stringify(prevValue)} → ${JSON.stringify(value)}` : '-'}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}
    </div>
  );
};
