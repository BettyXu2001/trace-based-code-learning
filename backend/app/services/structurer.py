from typing import List, Dict, Any, Optional

from app.models.schemas import ExecutionTrace, CompressedStep, StructuredTrace


class TraceStructurer:
    def __init__(self):
        self.threshold = 10

    def structure(self, raw_trace: ExecutionTrace) -> StructuredTrace:
        compressed_steps = self.compress_loops(raw_trace, self.threshold)
        execution_path = self._build_execution_path(compressed_steps)
        key_nodes = self._identify_key_nodes(compressed_steps)
        path_summary = self._generate_path_summary(compressed_steps)
        return StructuredTrace(
            compressed_steps=compressed_steps,
            execution_path=execution_path,
            key_nodes=key_nodes,
            path_summary=path_summary
        )

    def compress_loops(self, trace: ExecutionTrace, threshold: int = 10) -> List[CompressedStep]:
        """Compress loop iterations, return list of CompressedStep"""
        if not trace.steps:
            return []

        compressed_steps: List[CompressedStep] = []
        i = 0
        n = len(trace.steps)
        step_id_counter = 0

        while i < n:
            current_step = trace.steps[i]
            if current_step.line == 0:
                # Handle special steps
                compressed_steps.append(CompressedStep(
                    step_id=step_id_counter,
                    line=current_step.line,
                    code=current_step.code,
                    vars_snapshot=current_step.vars_after,
                    node_type="normal"
                ))
                i += 1
                step_id_counter += 1
                continue

            repeat_count = 1
            j = i + 1
            while j < n and trace.steps[j].line == current_step.line:
                repeat_count += 1
                j += 1

            if repeat_count >= threshold:
                new_step = CompressedStep(
                    step_id=step_id_counter,
                    line=current_step.line,
                    code=current_step.code,
                    vars_snapshot=current_step.vars_after,
                    node_type="loop_start",
                    iteration_count=repeat_count
                )
                compressed_steps.append(new_step)

                loop_end_step = CompressedStep(
                    step_id=step_id_counter + 1,
                    line=current_step.line,
                    code=f"  # Loop compressed: {repeat_count} iterations",
                    vars_snapshot=current_step.vars_after,
                    node_type="loop_end",
                    iteration_count=repeat_count
                )
                compressed_steps.append(loop_end_step)
                step_id_counter += 2
            else:
                for k in range(i, j):
                    step = trace.steps[k]
                    compressed_steps.append(CompressedStep(
                        step_id=step_id_counter,
                        line=step.line,
                        code=step.code,
                        vars_snapshot=step.vars_after,
                        node_type="normal"
                    ))
                    step_id_counter += 1

            i = j

        return compressed_steps

    def _build_execution_path(self, steps: List[CompressedStep]) -> List[int]:
        return [step.step_id for step in steps]

    def _identify_key_nodes(self, steps: List[CompressedStep]) -> Dict[str, List[int]]:
        key_nodes: Dict[str, List[int]] = {
            "loop_start": [],
            "loop_end": [],
            "branch": [],
            "merge": [],
            "call": [],
            "return": []
        }

        for step in steps:
            if step.node_type in key_nodes:
                key_nodes[step.node_type].append(step.step_id)

        return key_nodes

    def _generate_path_summary(self, steps: List[CompressedStep]) -> str:
        total_steps = len(steps)
        loop_count = sum(1 for s in steps if s.node_type in ("loop_start", "loop_end"))
        call_count = sum(1 for s in steps if s.node_type == "call")
        branch_count = sum(1 for s in steps if s.node_type == "branch")

        summary_parts = [f"Total steps: {total_steps}"]
        if loop_count > 0:
            summary_parts.append(f"Loops: {loop_count // 2}")
        if call_count > 0:
            summary_parts.append(f"Function calls: {call_count}")
        if branch_count > 0:
            summary_parts.append(f"Branches: {branch_count}")

        return ", ".join(summary_parts) if summary_parts else "No execution steps"
