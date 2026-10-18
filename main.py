"""FastAPI entry point for the single-page agentic to-do service."""

from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.responses import FileResponse
from pydantic import BaseModel, ConfigDict, Field

from agents.orchestrator import Orchestrator
from tools.repository import TaskRepository, TaskRepositoryTools


class TaskCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str = Field(min_length=1)
    priority: str = "normal"
    due_date: date | None = None
    completed: bool = False

    def normalized(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "priority": self.priority,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "completed": self.completed,
        }


class TaskUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str | None = Field(default=None, min_length=1)
    priority: str | None = None
    due_date: date | None = None
    completed: bool | None = None


class AssistantRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    text: str = Field(min_length=1)


def create_app(database: str | Path | None = None, provider: Any | None = None) -> FastAPI:
    repository = TaskRepository(database)
    tools = TaskRepositoryTools(repository)
    orchestrator = Orchestrator(tools, provider=provider)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        repository.initialize()
        yield

    app = FastAPI(title="Agentic To-Do App", lifespan=lifespan)
    app.state.repository = repository
    app.state.tools = tools
    app.state.orchestrator = orchestrator

    @app.get("/", response_class=FileResponse)
    def home() -> FileResponse:
        return FileResponse(Path(__file__).resolve().parent / "index.html", media_type="text/html")

    @app.get("/api/tasks")
    def list_tasks() -> list[dict[str, Any]]:
        return repository.list()

    @app.post("/api/tasks", status_code=201)
    def create_task(payload: TaskCreate) -> dict[str, Any]:
        try:
            values = payload.normalized()
            return repository.create(**values)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.get("/api/tasks/{task_id}")
    def get_task(task_id: int) -> dict[str, Any]:
        try:
            return repository.get(task_id)
        except LookupError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.patch("/api/tasks/{task_id}")
    def update_task(task_id: int, payload: TaskUpdate) -> dict[str, Any]:
        changes = payload.model_dump(exclude_unset=True)
        if "due_date" in changes and changes["due_date"] is not None:
            changes["due_date"] = changes["due_date"].isoformat()
        try:
            return repository.update(task_id, changes)
        except LookupError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.delete("/api/tasks/{task_id}", status_code=204)
    def delete_task(task_id: int) -> Response:
        try:
            repository.delete(task_id)
        except LookupError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return Response(status_code=204)

    @app.post("/api/assistant")
    def assistant(payload: AssistantRequest) -> dict[str, Any]:
        try:
            return orchestrator.handle(payload.text)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        except LookupError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.get("/api/plan/next")
    def next_task() -> dict[str, Any]:
        recommendation = orchestrator.planner_agent.suggest_next()
        return recommendation or {"task": None, "reason": "There are no pending tasks."}

    @app.get("/api/summary")
    def summary(for_date: date | None = Query(default=None, alias="date")) -> dict[str, Any]:
        return orchestrator.summary_agent.summarize(for_date)

    return app


app = create_app()
