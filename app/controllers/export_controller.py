import csv
import io
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.task import Task, TaskPriority, TaskStatus
from app.models.user import User


router = APIRouter(prefix="/tasks/export", tags=["Export"])


def _fetch_tasks(
    db: Session,
    user: User,
    include_assigned: bool,
    status_filter: TaskStatus | None,
    priority: TaskPriority | None,
) -> list[Task]:
    query = db.query(Task).filter(Task.deleted_at.is_(None))

    if include_assigned:
        query = query.filter(
            (Task.created_by_id == user.id) | (Task.assigned_to_id == user.id)
        )
    else:
        query = query.filter(Task.created_by_id == user.id)

    if status_filter is not None:
        query = query.filter(Task.status == status_filter)
    if priority is not None:
        query = query.filter(Task.priority == priority)

    return query.order_by(Task.created_at.desc()).all()


def _build_rows(tasks: list[Task]) -> list[dict]:
    return [
        {
            "ID": t.id,
            "Título": t.title,
            "Descrição": t.description or "",
            "Status": t.status.value,
            "Prioridade": t.priority.value,
            "Responsável (ID)": t.assigned_to_id or "",
            "Criado por (ID)": t.created_by_id,
            "Prazo": t.due_date.strftime("%d/%m/%Y %H:%M") if t.due_date else "",
            "Criado em": t.created_at.strftime("%d/%m/%Y %H:%M"),
            "Atualizado em": t.updated_at.strftime("%d/%m/%Y %H:%M"),
        }
        for t in tasks
    ]


@router.get("/csv")
def export_tasks_csv(
    include_assigned: bool = Query(False, alias="includeAssigned"),
    status_filter: TaskStatus | None = Query(None, alias="status"),
    priority: TaskPriority | None = Query(None, alias="priority"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StreamingResponse:
    tasks = _fetch_tasks(db, current_user, include_assigned, status_filter, priority)
    rows = _build_rows(tasks)

    output = io.StringIO()
    if rows:
        writer = csv.DictWriter(output, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    else:
        output.write("Nenhuma tarefa encontrada.")

    output.seek(0)
    filename = f"tarefas_{current_user.id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/pdf")
def export_tasks_pdf(
    include_assigned: bool = Query(False, alias="includeAssigned"),
    status_filter: TaskStatus | None = Query(None, alias="status"),
    priority: TaskPriority | None = Query(None, alias="priority"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StreamingResponse:
    from weasyprint import HTML

    tasks = _fetch_tasks(db, current_user, include_assigned, status_filter, priority)
    rows = _build_rows(tasks)

    if rows:
        tbody = "".join(
            "<tr>" + "".join(f"<td>{v}</td>" for v in r.values()) + "</tr>"
            for r in rows
        )
    else:
        tbody = '<tr><td colspan="10" class="empty">Nenhuma tarefa encontrada.</td></tr>'

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; font-size: 10px; padding: 24px; color: #111; }}
        h1 {{ font-size: 15px; margin: 0 0 4px; }}
        .meta {{ color: #555; margin-bottom: 20px; font-size: 9px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th {{
            background: #2563eb; color: #fff;
            padding: 6px 8px; text-align: left; font-size: 9px;
        }}
        td {{ padding: 5px 8px; border-bottom: 1px solid #e5e7eb; }}
        tr:nth-child(even) td {{ background: #f9fafb; }}
        .empty {{ text-align: center; padding: 16px; color: #888; }}
    </style>
    </head>
    <body>
        <h1>Relatório de Tarefas</h1>
        <p class="meta">
            Usuário ID: {current_user.id} &nbsp;|&nbsp;
            Gerado em: {datetime.utcnow().strftime('%d/%m/%Y %H:%M')} UTC
        </p>
        <table>
            <thead>
                <tr>
                    <th>ID</th><th>Título</th><th>Descrição</th><th>Status</th>
                    <th>Prioridade</th><th>Responsável</th><th>Criado por</th>
                    <th>Prazo</th><th>Criado em</th><th>Atualizado em</th>
                </tr>
            </thead>
            <tbody>{tbody}</tbody>
        </table>
    </body>
    </html>
    """

    pdf_bytes = HTML(string=html).write_pdf()
    filename = f"tarefas_{current_user.id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )