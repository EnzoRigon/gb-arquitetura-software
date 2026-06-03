from fastapi import FastAPI

from app.controllers.auth_controller import router as auth_router
from app.controllers.notification_controller import router as notification_router
from app.controllers.task_controller import router as task_router
from app.controllers.user_controller import router as user_router
from app.database import engine
from app.models.base import Base
from app.controllers.export_controller import router as export_router


app = FastAPI(
    title="Task Management API",
    description="API RESTful de Gestao de Tarefas Colaborativas (MVC + FastAPI)",
    version="1.0.0",
)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


app.include_router(auth_router)
app.include_router(user_router)
app.include_router(task_router)
app.include_router(notification_router)
app.include_router(export_router)


@app.get("/health", tags=["Health"])
def health() -> dict[str, str]:
    return {"status": "ok"}
