from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.task import Task, TaskPriority, TaskStatus
from app.models.user import User
from app.services.notification_service import notify_user, send_task_created_email
from app.views.task_view import TaskCreate, TaskResponse, TaskUpdate


router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    payload: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Task:
    assignee: User | None = None
    if payload.assigned_to_id is not None:
        assignee = db.query(User).filter(User.id == payload.assigned_to_id, User.is_active.is_(True)).first()
        if not assignee:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assigned user not found")

    task = Task(
        title=payload.title,
        description=payload.description,
        status=payload.status,
        priority=payload.priority,
        due_date=payload.due_date,
        assigned_to_id=payload.assigned_to_id,
        created_by_id=current_user.id,
    )
    db.add(task)

    if payload.assigned_to_id is not None:
        notify_user(
            db,
            payload.assigned_to_id,
            f"Voce recebeu uma nova tarefa: '{payload.title}'.",
        )
        if assignee:
            send_task_created_email(to_email=assignee.email, task_title=payload.title)

    db.commit()
    db.refresh(task)
    return task


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> Task:
    task = db.query(Task).filter(Task.id == task_id, Task.deleted_at.is_(None)).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.get("", response_model=list[TaskResponse])
def list_tasks(
    assigned_to: int | None = Query(default=None, alias="assignedTo"),
    status_filter: TaskStatus | None = Query(default=None, alias="status"),
    priority: TaskPriority | None = Query(default=None, alias="priority"),
    due_before: datetime | None = Query(default=None, alias="dueBefore"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[Task]:
    query = db.query(Task).filter(Task.deleted_at.is_(None))

    if assigned_to is not None:
        query = query.filter(Task.assigned_to_id == assigned_to)
    if status_filter is not None:
        query = query.filter(Task.status == status_filter)
    if priority is not None:
        query = query.filter(Task.priority == priority)
    if due_before is not None:
        query = query.filter(Task.due_date.is_not(None), Task.due_date <= due_before)

    return query.order_by(Task.created_at.desc()).all()


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Task:
    task = db.query(Task).filter(Task.id == task_id, Task.deleted_at.is_(None)).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    previous_assignee = task.assigned_to_id
    changed_fields: list[str] = []

    if payload.assigned_to_id is not None and payload.assigned_to_id != task.assigned_to_id:
        assignee = db.query(User).filter(User.id == payload.assigned_to_id, User.is_active.is_(True)).first()
        if not assignee:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assigned user not found")
        task.assigned_to_id = payload.assigned_to_id
        changed_fields.append("assigned_to_id")

    if payload.title is not None and payload.title != task.title:
        task.title = payload.title
        changed_fields.append("title")
    if payload.description is not None and payload.description != task.description:
        task.description = payload.description
        changed_fields.append("description")
    if payload.status is not None and payload.status != task.status:
        task.status = payload.status
        changed_fields.append("status")
    if payload.priority is not None and payload.priority != task.priority:
        task.priority = payload.priority
        changed_fields.append("priority")
    if payload.due_date is not None and payload.due_date != task.due_date:
        task.due_date = payload.due_date
        changed_fields.append("due_date")

    if changed_fields and task.assigned_to_id is not None:
        changed_info = ", ".join(changed_fields)
        notify_user(
            db,
            task.assigned_to_id,
            f"A tarefa '{task.title}' foi alterada ({changed_info}) por usuario {current_user.id}.",
        )

    if (
        previous_assignee is not None
        and previous_assignee != task.assigned_to_id
        and task.assigned_to_id is not None
    ):
        notify_user(
            db,
            task.assigned_to_id,
            f"A tarefa '{task.title}' foi atribuida a voce.",
        )

    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> dict[str, str]:
    task = db.query(Task).filter(Task.id == task_id, Task.deleted_at.is_(None)).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    task.deleted_at = datetime.utcnow()
    db.commit()
    return {"message": "Task deleted successfully"}
