"""
Vyom - Parallel Multi-Agent Execution
Multiple subtasks ko ek saath (parallel) chalata hai.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed


class ParallelAgentExecutor:
    def __init__(self, agent_router, max_workers=4):
        self.agent_router = agent_router
        self.max_workers = max_workers

    def run_tasks_parallel(self, tasks):
        results = [None] * len(tasks)

        def _run_one(index, task):
            agent = self.agent_router.route(task)
            agent_name = agent.name if agent else "general"
            try:
                answer = self.agent_router.handle(task)
                return {"index": index, "task": task, "agent": agent_name, "ok": True, "answer": answer}
            except Exception as e:
                return {"index": index, "task": task, "agent": agent_name, "ok": False, "error": str(e)}

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(_run_one, i, t): i for i, t in enumerate(tasks)}
            for future in as_completed(futures):
                result = future.result()
                results[result["index"]] = result

        return results

    def run_plan_parallel(self, subtask_titles):
        return self.run_tasks_parallel(subtask_titles)
