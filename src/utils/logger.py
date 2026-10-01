"""
Logger utilities for Agent-Infra-V1.0.1

Enhanced logging with protocol generation and file management.
"""

import logging
import sys
import os
from typing import Optional, List, Dict, Any
from pathlib import Path
from datetime import datetime
import json


# Ensure logs directory exists
LOGS_DIR = Path(__file__).parent.parent.parent / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)


def setup_logger(
    name: str = "AgentInfra",
    log_level: int = logging.INFO,
    log_file: Optional[str] = None,
    console: bool = True,
    protocol: bool = True
) -> logging.Logger:
    """
    Setup a logger with file and console handlers.
    
    Args:
        name: Name of the logger
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (optional)
        console: Whether to output to console
        protocol: Whether to generate work protocols
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Add console handler
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # Add file handler
    if log_file:
        # Ensure directory exists
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Add protocol handler if enabled
    if protocol:
        protocol_handler = ProtocolHandler(logger)
        logger.addHandler(protocol_handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger


def get_logger(name: str = "AgentInfra") -> logging.Logger:
    """
    Get a logger instance.
    
    Args:
        name: Name of the logger
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class ProtocolHandler(logging.Handler):
    """
    Custom handler for generating work protocols.
    
    Creates structured log entries that can be saved as work protocols.
    """
    
    def __init__(self, logger: logging.Logger):
        super().__init__()
        self.logger = logger
        self.protocol_entries: List[Dict[str, Any]] = []
        self.current_session: Dict[str, Any] = {
            "start_time": datetime.now().isoformat(),
            "entries": []
        }
    
    def emit(self, record: logging.LogRecord):
        """Emit a log record and add to protocol"""
        try:
            # Format the message
            msg = self.format(record)
            
            # Create protocol entry
            entry = {
                "timestamp": datetime.now().isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": msg,
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno
            }
            
            # Add to current session
            self.current_session["entries"].append(entry)
            self.protocol_entries.append(entry)
            
        except Exception as e:
            self.handleError(record)
    
    def save_protocol(self, session_name: str = None) -> str:
        """
        Save the current protocol session to a file.
        
        Args:
            session_name: Name for the session (defaults to timestamp)
            
        Returns:
            Path to the saved protocol file
        """
        if not session_name:
            session_name = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # End the current session
        self.current_session["end_time"] = datetime.now().isoformat()
        self.current_session["duration_seconds"] = (
            datetime.fromisoformat(self.current_session["end_time"]) -
            datetime.fromisoformat(self.current_session["start_time"])
        ).total_seconds()
        
        # Create protocol data
        protocol_data = {
            "session": self.current_session,
            "entries": self.protocol_entries
        }
        
        # Save to file
        filename = f"protocol_{session_name}.json"
        filepath = LOGS_DIR / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(protocol_data, f, indent=2, ensure_ascii=False)
            
            # Start new session
            self.current_session = {
                "start_time": datetime.now().isoformat(),
                "entries": []
            }
            self.protocol_entries = []
            
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Failed to save protocol: {e}")
            return ""
    
    def save_protocol_text(self, session_name: str = None) -> str:
        """
        Save the current protocol session as a text file.
        
        Args:
            session_name: Name for the session (defaults to timestamp)
            
        Returns:
            Path to the saved protocol file
        """
        if not session_name:
            session_name = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # End the current session
        self.current_session["end_time"] = datetime.now().isoformat()
        
        # Create text content
        lines = [
            "=" * 80,
            "WORK PROTOCOL - Agent-Infra-V1.0.1",
            "=" * 80,
            f"Session: {session_name}",
            f"Start Time: {self.current_session['start_time']}",
            f"End Time: {self.current_session['end_time']}",
            f"Duration: {self.current_session.get('duration_seconds', 0):.2f} seconds",
            "=" * 80,
            "",
            "PROTOCOL ENTRIES:",
            "-" * 80
        ]
        
        for entry in self.protocol_entries:
            lines.append(f"[{entry['timestamp']}] {entry['level']} - {entry['message']}")
        
        lines.extend([
            "-" * 80,
            f"Total Entries: {len(self.protocol_entries)}",
            "=" * 80
        ])
        
        # Save to file
        filename = f"protocol_{session_name}.txt"
        filepath = LOGS_DIR / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            
            # Start new session
            self.current_session = {
                "start_time": datetime.now().isoformat(),
                "entries": []
            }
            self.protocol_entries = []
            
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Failed to save text protocol: {e}")
            return ""


class AgentLogger:
    """
    Custom logger class for the International Standards Agent.
    
    Supports work protocol generation and comprehensive logging.
    """
    
    def __init__(
        self,
        name: str = "InternationalStandardsAgent",
        log_level: int = logging.INFO,
        log_file: Optional[str] = None,
        protocol_enabled: bool = True
    ):
        self.logger = setup_logger(
            name, 
            log_level, 
            log_file,
            protocol=protocol_enabled
        )
        self.debug_info: List[Dict[str, Any]] = []
        self.protocol_handler: Optional[ProtocolHandler] = None
        self.protocol_enabled = protocol_enabled
        
        # Find the protocol handler
        for handler in self.logger.handlers:
            if isinstance(handler, ProtocolHandler):
                self.protocol_handler = handler
                break
    
    def debug(self, message: str):
        """Log debug message"""
        self.logger.debug(message)
        self.debug_info.append({"level": "debug", "message": message, "timestamp": datetime.now().isoformat()})
    
    def info(self, message: str):
        """Log info message"""
        self.logger.info(message)
        self.debug_info.append({"level": "info", "message": message, "timestamp": datetime.now().isoformat()})
    
    def warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)
        self.debug_info.append({"level": "warning", "message": message, "timestamp": datetime.now().isoformat()})
    
    def error(self, message: str):
        """Log error message"""
        self.logger.error(message)
        self.debug_info.append({"level": "error", "message": message, "timestamp": datetime.now().isoformat()})
    
    def critical(self, message: str):
        """Log critical message"""
        self.logger.critical(message)
        self.debug_info.append({"level": "critical", "message": message, "timestamp": datetime.now().isoformat()})
    
    def get_debug_info(self) -> list:
        """Get collected debug information"""
        return self.debug_info.copy()
    
    def clear_debug_info(self):
        """Clear collected debug information"""
        self.debug_info.clear()
    
    def save_protocol(self, session_name: str = None) -> str:
        """
        Save the current work protocol.
        
        Args:
            session_name: Name for the protocol session
            
        Returns:
            Path to the saved protocol file
        """
        if self.protocol_handler:
            return self.protocol_handler.save_protocol(session_name)
        return ""
    
    def save_protocol_text(self, session_name: str = None) -> str:
        """
        Save the current work protocol as text.
        
        Args:
            session_name: Name for the protocol session
            
        Returns:
            Path to the saved protocol file
        """
        if self.protocol_handler:
            return self.protocol_handler.save_protocol_text(session_name)
        return ""


class WorkProtocolManager:
    """
    Manager for work protocols and logging sessions.
    """
    
    def __init__(self, logs_dir: str = None):
        """
        Initialize the work protocol manager.
        
        Args:
            logs_dir: Directory to store protocol files
        """
        self.logs_dir = Path(logs_dir) if logs_dir else LOGS_DIR
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.current_session: Dict[str, Any] = {
            "start_time": datetime.now().isoformat(),
            "entries": []
        }
        self.sessions: List[Dict[str, Any]] = []
    
    def add_entry(
        self,
        level: str,
        message: str,
        logger_name: str = "AgentInfra",
        module: str = "",
        function: str = "",
        line: int = 0
    ):
        """
        Add an entry to the current session.
        
        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            message: Log message
            logger_name: Name of the logger
            module: Module name
            function: Function name
            line: Line number
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "logger": logger_name,
            "message": message,
            "module": module,
            "function": function,
            "line": line
        }
        
        self.current_session["entries"].append(entry)
    
    def end_session(self) -> Dict[str, Any]:
        """
        End the current session and return it.
        
        Returns:
            The completed session data
        """
        self.current_session["end_time"] = datetime.now().isoformat()
        self.current_session["duration_seconds"] = (
            datetime.fromisoformat(self.current_session["end_time"]) -
            datetime.fromisoformat(self.current_session["start_time"])
        ).total_seconds()
        
        session = self.current_session
        self.sessions.append(session)
        
        # Start new session
        self.current_session = {
            "start_time": datetime.now().isoformat(),
            "entries": []
        }
        
        return session
    
    def save_session(self, session: Dict[str, Any], name: str = None) -> str:
        """
        Save a session to a file.
        
        Args:
            session: Session data to save
            name: Name for the session file
            
        Returns:
            Path to the saved file
        """
        if not name:
            name = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save as JSON
        json_filename = f"session_{name}.json"
        json_path = self.logs_dir / json_filename
        
        try:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(session, f, indent=2, ensure_ascii=False)
            return str(json_path)
        except Exception as e:
            print(f"Error saving session: {e}")
            return ""
    
    def save_session_text(self, session: Dict[str, Any], name: str = None) -> str:
        """
        Save a session as a text file.
        
        Args:
            session: Session data to save
            name: Name for the session file
            
        Returns:
            Path to the saved file
        """
        if not name:
            name = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create text content
        lines = [
            "=" * 80,
            "WORK SESSION PROTOCOL - Agent-Infra-V1.0.1",
            "=" * 80,
            f"Session: {name}",
            f"Start Time: {session['start_time']}",
            f"End Time: {session['end_time']}",
            f"Duration: {session.get('duration_seconds', 0):.2f} seconds",
            f"Total Entries: {len(session['entries'])}",
            "=" * 80,
            "",
            "SESSION ENTRIES:",
            "-" * 80
        ]
        
        for entry in session["entries"]:
            lines.append(f"[{entry['timestamp']}] {entry['level']} - {entry['message']}")
        
        lines.extend([
            "-" * 80,
            "END OF SESSION",
            "=" * 80
        ])
        
        # Save to file
        txt_filename = f"session_{name}.txt"
        txt_path = self.logs_dir / txt_filename
        
        try:
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            return str(txt_path)
        except Exception as e:
            print(f"Error saving session text: {e}")
            return ""
    
    def list_sessions(self) -> List[str]:
        """
        List all saved session files.
        
        Returns:
            List of session file paths
        """
        session_files = []
        
        for ext in ['*.json', '*.txt']:
            session_files.extend(self.logs_dir.glob(ext))
        
        return [str(f) for f in sorted(session_files)]
    
    def get_session(self, filepath: str) -> Optional[Dict[str, Any]]:
        """
        Load a session from a file.
        
        Args:
            filepath: Path to the session file
            
        Returns:
            Session data or None if error
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading session: {e}")
            return None


# Global protocol manager
protocol_manager = WorkProtocolManager()


# Convenience functions
def start_protocol_session(name: str = None) -> str:
    """
    Start a new protocol session.
    
    Args:
        name: Optional name for the session
        
    Returns:
        Session ID
    """
    if name:
        protocol_manager.current_session["name"] = name
    return protocol_manager.current_session.get("name", protocol_manager.current_session["start_time"])


def end_protocol_session(name: str = None) -> str:
    """
    End the current protocol session and save it.
    
    Args:
        name: Name for the session file
        
    Returns:
        Path to the saved session file
    """
    session = protocol_manager.end_session()
    if name:
        return protocol_manager.save_session(session, name)
    return protocol_manager.save_session(session)


def log_to_protocol(
    level: str,
    message: str,
    logger_name: str = "AgentInfra",
    module: str = "",
    function: str = "",
    line: int = 0
):
    """
    Add a log entry to the current protocol session.
    
    Args:
        level: Log level
        message: Message to log
        logger_name: Logger name
        module: Module name
        function: Function name
        line: Line number
    """
    protocol_manager.add_entry(level, message, logger_name, module, function, line)
