import React from 'react';
import type { CompressedStep } from '../types';

interface ExecutionTimelineProps {
  steps: CompressedStep[];
  currentStep: number;
  onStepClick: (stepId: number) => void;
}

export const ExecutionTimeline: React.FC<ExecutionTimelineProps> = ({
  steps,
  currentStep,
  onStepClick,
}) => {
  return (
    <div className="execution-timeline">
      <h3>执行时间轴</h3>
      <div className="timeline-steps">
        {steps.map((step, index) => (
          <div
            key={step.step_id}
            className={`timeline-step ${step.node_type} ${currentStep === step.step_id ? 'active' : ''}`}
            onClick={() => onStepClick(step.step_id)}
          >
            <div className="step-number">{index + 1}</div>
            <div className="step-content">
              <span className="step-line">L{step.line}</span>
              <span className="step-code">{step.code.substring(0, 30)}...</span>
              {step.node_type === 'loop_start' && (
                <span className="step-badge loop">循环</span>
              )}
              {step.node_type === 'branch' && step.branch_taken && (
                <span className="step-badge branch">{step.branch_taken}</span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
