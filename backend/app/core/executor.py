from backend.app.models.task import Task


class Executor:
    def execute_task(self, task: Task) -> Task:
        try:
            task.status = "in_progress"

            if task.subtasks:
                for subtask in task.subtasks:
                    self.execute_task(subtask)

                failed_tasks = [
                    subtask
                    for subtask in task.subtasks
                    if subtask.status == "failed"
                ]

                if failed_tasks:
                    task.fail(
                        f"{len(failed_tasks)} subtask(s) failed."
                    )
                else:
                    task.complete(
                        "All subtasks completed successfully."
                    )

            else:
                task.complete(
                    f"Task completed: {task.description}"
                )

        except Exception as error:
            task.fail(str(error))

        return task