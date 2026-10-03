import logging
from typing import Dict, List, Any, Optional
import subprocess
import os
import json

logger = logging.getLogger(__name__)

class WindowsAutomation:
    """Windows task and system automation"""
    
    def __init__(self):
        self.platform = self._detect_platform()
    
    def _detect_platform(self) -> str:
        """Detect OS"""
        import platform
        return platform.system()
    
    def run_command(self, command: str, shell: bool = True) -> Dict[str, Any]:
        """Run system command"""
        try:
            result = subprocess.run(command, shell=shell, capture_output=True, text=True, timeout=30)
            return {
                'status': 'success',
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
        except subprocess.TimeoutExpired:
            return {'status': 'timeout', 'message': 'Command execution timed out'}
        except Exception as e:
            logger.error(f"Command execution error: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def open_application(self, app_name: str) -> bool:
        """Open application"""
        try:
            if self.platform == 'Windows':
                os.startfile(app_name)
            elif self.platform == 'Darwin':  # macOS
                subprocess.Popen(['open', app_name])
            else:  # Linux
                subprocess.Popen([app_name])
            logger.info(f"Opened application: {app_name}")
            return True
        except Exception as e:
            logger.error(f"App open error: {e}")
            return False
    
    def create_scheduled_task(self, task_name: str, command: str, trigger: str = 'DAILY') -> Dict[str, Any]:
        """Create scheduled task (Windows only)"""
        if self.platform != 'Windows':
            return {'status': 'error', 'message': 'Only available on Windows'}
        
        try:
            # PowerShell command to create scheduled task
            ps_command = f"""
            $action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument '-Command "{command}"'
            $trigger = New-ScheduledTaskTrigger -{trigger}
            Register-ScheduledTask -TaskName '{task_name}' -Action $action -Trigger $trigger
            """
            result = self.run_command(ps_command)
            logger.info(f"Task created: {task_name}")
            return result
        except Exception as e:
            logger.error(f"Task creation error: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def get_process_list(self) -> List[str]:
        """Get list of running processes"""
        try:
            if self.platform == 'Windows':
                result = self.run_command('tasklist')
            else:
                result = self.run_command('ps aux')
            return result['stdout'].split('\n')
        except Exception as e:
            logger.error(f"Process list error: {e}")
            return []
    
    def kill_process(self, process_name: str) -> bool:
        """Kill a process"""
        try:
            if self.platform == 'Windows':
                self.run_command(f'taskkill /IM {process_name} /F')
            else:
                self.run_command(f'killall {process_name}')
            logger.info(f"Killed process: {process_name}")
            return True
        except Exception as e:
            logger.error(f"Kill process error: {e}")
            return False
    
    def set_environment_variable(self, key: str, value: str) -> bool:
        """Set environment variable"""
        try:
            os.environ[key] = value
            logger.info(f"Environment variable set: {key}")
            return True
        except Exception as e:
            logger.error(f"Env var set error: {e}")
            return False
    
    def file_operations(self, operation: str, source: str, destination: str = None) -> Dict[str, Any]:
        """File operations (copy, move, delete)"""
        try:
            if operation == 'copy':
                import shutil
                shutil.copy(source, destination)
                return {'status': 'success', 'operation': 'copy'}
            elif operation == 'move':
                import shutil
                shutil.move(source, destination)
                return {'status': 'success', 'operation': 'move'}
            elif operation == 'delete':
                os.remove(source)
                return {'status': 'success', 'operation': 'delete'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        try:
            import psutil
            return {
                'platform': self.platform,
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
                'cpu_count': psutil.cpu_count(),
                'total_memory': psutil.virtual_memory().total
            }
        except Exception as e:
            logger.error(f"System info error: {e}")
            return {'status': 'error', 'message': str(e)}

if __name__ == '__main__':
    logger.info("Windows automation module ready")
