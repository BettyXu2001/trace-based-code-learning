export type NodeType = 'normal' | 'loop_start' | 'loop_end' | 'branch' | 'merge' | 'call' | 'return';
export type LearningType = 'function' | 'class' | 'module';

export interface FunctionInfo {
  name: string;
  lineno: number;
  end_lineno: number;
  args: string[];
  docstring?: string;
}

export interface ClassInfo {
  name: string;
  lineno: number;
  end_lineno: number;
  methods: string[];
  docstring?: string;
}

export interface LearningUnit {
  name: string;
  type: LearningType;
  lineno: number;
  content: string;
  depends_on: string[];
}

export interface CodeStructure {
  functions: FunctionInfo[];
  classes: ClassInfo[];
  dependencies: Record<string, string[]>;
  learning_path: string[];
  learning_units: LearningUnit[];
}

export interface TraceStep {
  step_id: number;
  line: number;
  code: string;
  vars_before: Record<string, unknown>;
  vars_after: Record<string, unknown>;
  event: string;
  function_name: string;
}

export interface ErrorInfo {
  type: string;
  message: string;
  traceback: TraceStep[];
}

export interface ExecutionTrace {
  steps: TraceStep[];
  variables: Record<string, unknown>;
  call_stack: string[];
  exception?: ErrorInfo;
}

export interface CompressedStep {
  step_id: number;
  line: number;
  code: string;
  vars_snapshot: Record<string, unknown>;
  node_type: NodeType;
  iteration_count?: number;
  branch_taken?: string;
}

export interface StructuredTrace {
  compressed_steps: CompressedStep[];
  execution_path: number[];
  key_nodes: Record<NodeType, number[]>;
  path_summary: string;
}

export interface StepExplanation {
  step_id: number;
  line: number;
  project_meaning: string;
  element_meaning: string;
  citation: string;
}

export interface VariableChangeExplanation {
  var_name: string;
  old_value: unknown;
  new_value: unknown;
  reason: string;
}

export interface Explanation {
  summary: string;
  step_explanations: StepExplanation[];
  variable_changes: VariableChangeExplanation[];
  key_insights: string[];
}

export interface Lesson {
  id: number;
  title: string;
  type: LearningType;
  content: string;
  explanation: Explanation;
  trace?: StructuredTrace;
  key_insights: string[];
}

export interface Course {
  title: string;
  description: string;
  lessons: Lesson[];
  total_steps: number;
}

export interface AnalyzeResponse {
  code_structure: CodeStructure;
  trace: ExecutionTrace;
  structured_trace: StructuredTrace;
  explanation: Explanation;
}

export interface CourseResponse {
  course: Course;
}
