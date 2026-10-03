import logging
import sys
import time
from io import StringIO
from typing import Any, Dict, Tuple

from RestrictedPython import compile_restricted

logger = logging.getLogger(__name__)


class SandboxExecutor:
    def __init__(self, timeout: int = 30):
        self.timeout = timeout

    def execute(self, code: str, context: Dict[str, Any] | None = None) -> Tuple[bool, str, float]:
        start = time.time()
        try:
            compiled = compile_restricted(code, '<string>', 'exec')
            if getattr(compiled, 'errors', None):
                return False, f'Compile error: {compiled.errors}', time.time() - start

            safe_globals = {'__builtins__': {'print': print, 'range': range, 'len': len, 'str': str, 'int': int, 'float': float, 'list': list, 'dict': dict, 'sum': sum, 'min': min, 'max': max, 'abs': abs, 'sorted': sorted, 'enumerate': enumerate, 'zip': zip}}
            if context:
                safe_globals.update(context)

            buffer = StringIO()
            original_stdout = sys.stdout
            sys.stdout = buffer
            try:
                exec(compiled.code, safe_globals)
            finally:
                sys.stdout = original_stdout

            data = buffer.getvalue()
            elapsed = time.time() - start
            return True, data, elapsed

        except Exception as exc:
            sys.stdout = sys.__stdout__
            return False, f'Runtime error: {exc}', time.time() - start


class CodeGenerator:
    def __init__(self, ai_manager):
        self.ai_manager = ai_manager
        self.sandbox = SandboxExecutor()

    async def generate_code(self, instruction: str):
        prompt = f"""Generate valid Python code only.

Task:
{instruction}

Rules:
- no markdown
- no explanations
- include basic error handling
- keep it clean and runnable
"""
        code = await self.ai_manager.generate_text(prompt, temperature=0.2, max_tokens=2000)
        return {'instruction': instruction, 'code': code, 'status': 'generated'}

    async def generate_and_execute(self, instruction: str):
        generated = await self.generate_code(instruction)
        code = generated['code']
        success, output, elapsed = self.sandbox.execute(code)
        generated['success'] = success
        generated['output'] = output
        generated['execution_time'] = elapsed
        return generated
