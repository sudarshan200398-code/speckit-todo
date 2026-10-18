from agents.task_agent import TaskAgent
from tools.repository import TaskRepositoryTools


def test_task_agent_delegates_all_data_access_to_tools(repository):
    tools = TaskRepositoryTools(repository)
    agent = TaskAgent(tools)

    task = agent.create("Buy milk")
    task = agent.complete(task["id"])
    assert task["completed"] is True
    task = agent.reopen(task["id"])
    assert task["completed"] is False
    agent.delete(task["id"])
