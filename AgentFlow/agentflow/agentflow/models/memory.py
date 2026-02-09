from typing import Dict, Any, List, Union, Optional
import os

class Memory:

    def __init__(self):
        self.query: Optional[str] = None
        self.files: List[Dict[str, str]] = []
        self.actions: Dict[str, Dict[str, Any]] = {}
        self._init_file_types()

    def set_query(self, query: str) -> None:
        if not isinstance(query, str):
            raise TypeError("Query must be a string")
        self.query = query

    def _init_file_types(self):
        self.file_types = {
            'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp'],
            'text': ['.txt', '.md'],
            'document': ['.pdf', '.doc', '.docx'],
            'code': ['.py', '.js', '.java', '.cpp', '.h'],
            'data': ['.json', '.csv', '.xml'],
            'spreadsheet': ['.xlsx', '.xls'],
            'presentation': ['.ppt', '.pptx'],
        }
        self.file_type_descriptions = {
            'image': "An image file ({ext} format) provided as context for the query",
            'text': "A text file ({ext} format) containing additional information related to the query",
            'document': "A document ({ext} format) with content relevant to the query",
            'code': "A source code file ({ext} format) potentially related to the query",
            'data': "A data file ({ext} format) containing structured data pertinent to the query",
            'spreadsheet': "A spreadsheet file ({ext} format) with tabular data relevant to the query",
            'presentation': "A presentation file ({ext} format) with slides related to the query",
        }

    def _get_default_description(self, file_name: str) -> str:
        _, ext = os.path.splitext(file_name)
        ext = ext.lower()

        for file_type, extensions in self.file_types.items():
            if ext in extensions:
                return self.file_type_descriptions[file_type].format(ext=ext[1:])

        return f"A file with {ext[1:]} extension, provided as context for the query"
    
    def add_file(self, file_name: Union[str, List[str]], description: Union[str, List[str], None] = None) -> None:
        if isinstance(file_name, str):
            file_name = [file_name]
        
        if description is None:
            description = [self._get_default_description(fname) for fname in file_name]
        elif isinstance(description, str):
            description = [description]
        
        if len(file_name) != len(description):
            raise ValueError("The number of files and descriptions must match.")
        
        for fname, desc in zip(file_name, description):
            self.files.append({
                'file_name': fname,
                'description': desc
            })

    def add_action(self, step_count: int, tool_name: str, sub_goal: str, command: str, result: Any) -> None:
        # Truncate command to first 100 characters to save memory
        truncated_command = command[:100] + "..." if len(command) > 100 else command

        action = {
            'tool_name': tool_name,
            'sub_goal': sub_goal,
            'command': truncated_command,
            'result': result,
        }
        step_name = f"Action Step {step_count}"
        self.actions[step_name] = action

    def mark_start_again(self, step_count: int, reason: str, clear_history: bool = False) -> None:
        """Mark a START_AGAIN signal in memory.

        Args:
            step_count: Current step number.
            reason: Why the pipeline is being restarted.
            clear_history: If True, clear all prior actions and start fresh.
                           If False, keep prior actions but add a START_AGAIN marker
                           so subsequent tools know to ignore everything before it.
        """
        if clear_history:
            self.actions.clear()

        action = {
            'tool_name': 'Start_Again_Tool',
            'sub_goal': 'Restart pipeline from scratch',
            'command': 'Pipeline restart',
            'result': f'START_AGAIN: {reason}. All operations before this point should be discarded.',
        }
        step_name = f"Action Step {step_count}"
        self.actions[step_name] = action

    def get_query(self) -> Optional[str]:
        return self.query

    def get_files(self) -> List[Dict[str, str]]:
        return self.files
    
    def get_actions(self) -> Dict[str, Dict[str, Any]]:
        return self.actions
    