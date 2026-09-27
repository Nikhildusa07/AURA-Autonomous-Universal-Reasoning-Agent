from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Task:
    id: int
    description: str
    status: str = "pending"
    priority: int = 1
    parent_id: Optional[int] = None
    result: Optional[str] = None
    error: Optional[str] = None
    subtasks: list["Task"] = field(default_factory=list)

    def complete(self, result: str):
        self.status = "completed"
        self.result = result

    def fail(self, error: str):
        self.status = "failed"
        self.error = error

    def add_subtask(self, task: "Task"):
        self.subtasks.append(task)