import React from 'react';
import type { Explanation } from '../types';

interface ExplanationPanelProps {
  explanation: Explanation;
  currentStep?: number;
}

export const ExplanationPanel: React.FC<ExplanationPanelProps> = ({
  explanation,
  currentStep,
}) => {
  return (
    <div className="explanation-content">
      <div className="summary">
        <h4>执行摘要</h4>
        <p>{explanation.summary}</p>
      </div>

      <div className="step-explanations">
        <h4>分步解释</h4>
        {explanation.step_explanations.length === 0 ? (
          <p className="empty">{explanation.summary}</p>
        ) : (
          explanation.step_explanations.map((exp, index) => (
            <div
              key={index}
              className={`step-explanation ${currentStep === exp.step_id ? 'active' : ''}`}
            >
              <div className="explanation-header">
                <span className="citation">{exp.citation}</span>
                <span className="line">行 {exp.line}</span>
              </div>
              <div className="explanation-sections">
                <div className="explanation-section">
                  <h5>📖 项目含义</h5>
                  <p className="explanation-text">{exp.project_meaning}</p>
                </div>
                <div className="explanation-section">
                  <h5>🧩 元素含义</h5>
                  <p className="explanation-text">{exp.element_meaning}</p>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {explanation.variable_changes.length > 0 && (
        <div className="variable-changes">
          <h4>变量变化</h4>
          {explanation.variable_changes.map((vc, index) => (
            <div key={index} className="var-change">
              <span className="var-name">{vc.var_name}</span>
              <span className="var-values">
                {JSON.stringify(vc.old_value)} → {JSON.stringify(vc.new_value)}
              </span>
              <p className="var-reason">{vc.reason}</p>
            </div>
          ))}
        </div>
      )}

      {explanation.key_insights.length > 0 && (
        <div className="key-insights">
          <h4>关键洞察</h4>
          <ul>
            {explanation.key_insights.map((insight, index) => (
              <li key={index}>{insight}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};
