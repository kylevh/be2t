from typing import Callable, Dict, List

class StateManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        self._state = {
            'theme': {
                'primary_color': '#007bff',
                'background_color': '#ffffff',
                'text_color': '#000000'
            },
            'snapshots': {
                'all_projects': [],
                'all_dates': [],
                'current_project': None,
                'current_project_dates': [],
                'current_date': None,
                'current_snapshot': None,
            },
            'test_state': {
                'sub_test_state': "not updated",
                'sub_test_number': 0
            }
        }
        self._subscribers: Dict[str, List[Callable]] = {}
    
    def get_state(self, key=None):
        if key is None:
            return self._state
        
        # Handle nested keys
        keys = key.split('.')
        current = self._state
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return None
        return current
    
    def set_state(self, key, value):
        if isinstance(key, dict):
            # Handle dictionary updates
            self._state.update(key)
            # Notify for each updated key
            for k in key:
                self._notify_subscribers(k)
                # If the value is a dict, notify for all nested keys
                if isinstance(key[k], dict):
                    self._notify_nested_keys(k, key[k])
        else:
            # Handle nested keys like 'theme.primary_color'
            keys = key.split('.')
            current = self._state
            for k in keys[:-1]:
                current = current.setdefault(k, {})
            current[keys[-1]] = value
            # Notify subscribers
            self._notify_subscribers(key)
    
    def subscribe(self, key: str, callback: Callable):
        if key not in self._subscribers:
            self._subscribers[key] = []
        self._subscribers[key].append(callback)
        
    def unsubscribe(self, key: str, callback: Callable):
        if key in self._subscribers:
            self._subscribers[key].remove(callback)
    
    def _notify_subscribers(self, key: str):
        # Notify direct subscribers
        if key in self._subscribers:
            for callback in self._subscribers[key]:
                callback(self.get_state(key))
        
        # Notify parent key subscribers
        parts = key.split('.')
        while parts:
            parts.pop()
            parent_key = '.'.join(parts)
            if parent_key in self._subscribers:
                for callback in self._subscribers[parent_key]:
                    callback(self.get_state(parent_key))
    
    def _notify_nested_keys(self, parent_key: str, value_dict: dict):
        """Notify subscribers for all nested keys in a dictionary update"""
        for k, v in value_dict.items():
            nested_key = f"{parent_key}.{k}"
            self._notify_subscribers(nested_key)
            if isinstance(v, dict):
                self._notify_nested_keys(nested_key, v)