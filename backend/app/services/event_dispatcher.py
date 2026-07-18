import asyncio
from typing import Callable, Dict, List, Any
from app.logging.config import logger

class EventDispatcher:
    def __init__(self):
        # Maps event names to a list of asynchronous subscriber callbacks
        self._listeners: Dict[str, List[Callable[[Any], Any]]] = {}

    def register(self, event_type: str, listener: Callable[[Any], Any]) -> None:
        """Register an async callback listener for a specific event type."""
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(listener)
        logger.info("event_listener_registered", event=event_type, listener=listener.__name__)

    async def dispatch(self, event_type: str, data: Any) -> None:
        """Dispatch event payload to all registered listeners asynchronously."""
        if event_type not in self._listeners or not self._listeners[event_type]:
            return
            
        logger.info("event_dispatched_triggering_listeners", event=event_type, listener_count=len(self._listeners[event_type]))
        
        # Call all listener tasks concurrently
        tasks = [
            asyncio.create_task(listener(data))
            for listener in self._listeners[event_type]
        ]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

# Global singleton dispatcher instance
event_dispatcher = EventDispatcher()
