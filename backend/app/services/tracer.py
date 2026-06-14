import sys
import re
import builtins
import threading
from typing import Any, Optional, List, Dict
from io import StringIO

from app.models.schemas import ExecutionTrace, TraceStep, ErrorInfo


class SecurityError(Exception):
    pass


class TimeoutError(Exception):
    pass


class SecurityRestrictedbuiltins:
    """Restrict builtins for security"""
    _allowed = {
        'print': print,
        'len': len,
        'range': range,
        'str': str,
        'int': int,
        'float': float,
        'bool': bool,
        'list': list,
        'dict': dict,
        'tuple': tuple,
        'set': set,
        'abs': abs,
        'min': min,
        'max': max,
        'sum': sum,
        'sorted': sorted,
        'reversed': reversed,
        'enumerate': enumerate,
        'zip': zip,
        'map': map,
        'filter': filter,
        'isinstance': isinstance,
        'issubclass': issubclass,
        'hasattr': hasattr,
        'getattr': getattr,
        'setattr': setattr,
        'delattr': delattr,
        'dir': dir,
        'id': id,
        'hash': hash,
        'repr': repr,
        'round': round,
        'pow': pow,
        'divmod': divmod,
        'oct': oct,
        'hex': hex,
        'chr': chr,
        'ord': ord,
        'bin': bin,
        'slice': slice,
        'super': super,
        'type': type,
        'object': object,
        'Exception': Exception,
        'BaseException': BaseException,
        'ValueError': ValueError,
        'TypeError': TypeError,
        'IndexError': IndexError,
        'KeyError': KeyError,
        'ZeroDivisionError': ZeroDivisionError,
    }

    _blocked_attrs = {'__import__', '__builtins__', '__class__', '__subclasses__',
                      '__globals__', '__code__', '__closure__', '__func__'}

    def _validate_access(self, name: str) -> Any:
        """统一的安全检查逻辑"""
        if name in self._blocked_attrs:
            raise AttributeError(f"'{name}' is not allowed for security reasons")
        
        if name.startswith('_'):
            raise AttributeError(f"'{name}' is not allowed")
        
        if name in self._allowed:
            return self._allowed[name]
        
        raise AttributeError(f"'{name}' is not allowed")

    def __getitem__(self, name: str):
        return self._validate_access(name)

    def __getattr__(self, name: str):
        return self._validate_access(name)


class RuntimeTracer:
    def __init__(self, timeout_seconds: int = 5, max_memory_mb: int = 50):
        self.timeout_seconds = timeout_seconds
        self.max_memory_mb = max_memory_mb
        self._step_id = 0
        self._trace = ExecutionTrace()
        self._current_vars = {}
        self._vars_before_line = {}
        self._old_trace_func = None
        self._timeout_flag = False
        self._source_lines: Dict[int, str] = {}  # Store source lines by line number
        self._restricted_builtins = SecurityRestrictedbuiltins()
        self._blocked_attrs = SecurityRestrictedbuiltins._blocked_attrs.copy()

    def _pre_execution_check(self, code: str) -> None:
        """执行前的静态安全检查"""
        dangerous_patterns = [
            r'__import__',
            r'__builtins__',
            r'__class__\.__subclasses__',
            r'__globals__',
            r'eval\s*\(',
            r'exec\s*\(',
            r'compile\s*\(',
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, code):
                raise SecurityError(f"Potentially dangerous code detected: {pattern}")

    def _is_safe_value(self, value: Any) -> bool:
        """检查值是否安全"""
        if value is None or isinstance(value, (int, float, str, bool)):
            return True
        
        if isinstance(value, (list, tuple)):
            return all(self._is_safe_value(item) for item in value)
        
        if isinstance(value, dict):
            return all(
                isinstance(k, str) and not k.startswith('_') and self._is_safe_value(v)
                for k, v in value.items()
            )
        
        return False

    def _build_safe_scope(self, inputs: dict) -> dict:
        """构建安全的执行作用域"""
        scope = {
            '__builtins__': self._restricted_builtins,
        }
        
        if inputs:
            for key, value in inputs.items():
                if key.startswith('_') or key in self._blocked_attrs:
                    continue
                    
                if self._is_safe_value(value):
                    scope[key] = value
        
        return scope

    def trace(self, code: str, inputs: dict) -> ExecutionTrace:
        """Execute code with inputs and return trace"""
        self._step_id = 0
        self._trace = ExecutionTrace()
        self._current_vars = inputs.copy() if inputs else {}
        self._vars_before_line = self._current_vars.copy()
        self._current_frame = None
        self._timeout_flag = False

        try:
            self._pre_execution_check(code)
        except SecurityError as e:
            self._trace.exception = ErrorInfo(
                type="SecurityError",
                message=str(e),
                traceback=[]
            )
            return self._trace

        # Pre-load source lines for secure line lookup
        self._source_lines = {}
        for i, line in enumerate(code.splitlines(), start=1):
            self._source_lines[i] = line.strip()

        old_trace = sys.gettrace()
        timeout_timer = None

        def set_timeout():
            self._timeout_flag = True

        try:
            sys.settrace(self._trace_func)

            scope = self._build_safe_scope(inputs)

            old_stdout = sys.stdout
            old_stderr = sys.stderr
            sys.stdout = StringIO()
            sys.stderr = StringIO()

            # Cross-platform timeout using threading
            timeout_timer = threading.Timer(self.timeout_seconds, set_timeout)
            timeout_timer.start()

            try:
                exec(code, scope)
            except TimeoutError:
                self._trace.exception = ErrorInfo(
                    type="TimeoutError",
                    message=f"Execution exceeded {self.timeout_seconds} seconds",
                    traceback=self._trace.steps.copy()
                )
            except Exception as e:
                if not isinstance(self._trace.exception, ErrorInfo):
                    self._trace.exception = ErrorInfo(
                        type=type(e).__name__,
                        message=str(e),
                        traceback=self._trace.steps.copy()
                    )
            finally:
                if timeout_timer:
                    timeout_timer.cancel()
                sys.stdout = old_stdout
                sys.stderr = old_stderr

        finally:
            sys.settrace(old_trace)

        for key in list(scope.keys()):
            if not key.startswith('__') and key != 'builtins':
                try:
                    self._trace.variables[key] = scope[key]
                except:
                    pass

        if inputs:
            for k, v in inputs.items():
                if k in self._trace.variables:
                    self._trace.variables[k] = v

        return self._trace

    def _trace_func(self, frame, event: str, arg):
        """Trace function called on each event"""
        # Check timeout
        if self._timeout_flag:
            return None

        try:
            self._current_frame = frame
            code = frame.f_code
            function_name = code.co_name
            lineno = frame.f_lineno

            if event == 'call':
                self._trace.call_stack.append(function_name)
                self._vars_before_line = self._current_vars.copy()
            elif event == 'return':
                self._vars_before_line = self._current_vars.copy()
                if self._trace.call_stack:
                    self._trace.call_stack.pop()
            elif event in ('line', 'exception'):
                self._vars_before_line = self._current_vars.copy()

                # Use pre-loaded source lines instead of reading from file
                line_content = self._source_lines.get(lineno, self._get_line_content_fallback(lineno))

                vars_after = {}
                for key, value in frame.f_locals.items():
                    try:
                        if not callable(value) and not hasattr(value, '__code__'):
                            vars_after[key] = repr(value)
                        else:
                            vars_after[key] = f"<{type(value).__name__}>"
                    except:
                        vars_after[key] = f"<{type(value).__name__}>"

                self._current_vars = vars_after.copy()

                step = TraceStep(
                    step_id=self._step_id,
                    line=lineno,
                    code=line_content,
                    vars_before=self._vars_before_line.copy(),
                    vars_after=vars_after.copy(),
                    event=event,
                    function_name=function_name
                )
                self._trace.steps.append(step)
                self._step_id += 1

                if event == 'exception':
                    exc_type, exc_value, _ = arg
                    self._trace.exception = ErrorInfo(
                        type=exc_type.__name__ if exc_type else 'Exception',
                        message=str(exc_value) if exc_value else '',
                        traceback=self._trace.steps.copy()
                    )

            return self._trace_func

        except Exception:
            return self._trace_func

    def _get_line_content_fallback(self, lineno: int) -> str:
        """Fallback when line number is not in pre-loaded source"""
        return f"<line {lineno}>"
