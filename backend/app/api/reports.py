import uuid
from typing import Annotated

import aioboto3
from pathlib import Path

from botocore.exceptions import ClientError, NoCredentialsError
from fastapi import APIRouter, status, HTTPException, BackgroundTasks, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy import select

from backend.app.models import Report
from backend.schemas.reports import ReportGenerateRequest, ReportGenerateResponse
from backend.app.services.auth import db_dependency, get_current_user
from backend.app.core.config import settings
from backend.app.services.reports import generate_report_s3
import tempfile

router = APIRouter(prefix="/reports", tags=["reports"])
TEMP_DIR = Path(tempfile.gettempdir()) / "reports"
TEMP_DIR.mkdir(exist_ok=True)


@router.get("/get_user_reports")
async def get_user_reports(
        db: db_dependency,
        current_user: Annotated[dict, Depends(get_current_user)]):
    """
        Получить список всех отчетов текущего пользователя.

        Возвращает:
        - user_id: ID пользователя
        - reports: список отчетов с полями id, name, url

        Пример ответа:
        {
            "user_id": 21,
            "reports": [
                {"id": 1, "name": "report-abc123.xlsx", "url": "..."},
                {"id": 2, "name": "report-def456.pdf", "url": "..."}
            ]
        }

        Raises:
            HTTPException: 401 если нет учетных данных
        """
    try:
        query = select(Report).where(Report.user_id == int(current_user["user_id"]))
        result = await db.execute(query)
        reports = result.scalars().all()
        reports_data = [{
            "id": report.id,
            "name": report.name,
            "url": report.url
        } for report in reports]

        return {
            "user_id": current_user["user_id"],
            "reports": reports_data
        }
    except NoCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No credentials provided",
        )


@router.post("/generate", response_model=ReportGenerateResponse, status_code=status.HTTP_202_ACCEPTED)
async def generate_report(
        payload: ReportGenerateRequest,
        background_tasks: BackgroundTasks,
        db: db_dependency,
        current_user: Annotated[dict, Depends(get_current_user)]
):
    """
    Асинхронно генерирует отчет в фоне (Excel/PDF) и сохраняет в VK Cloud S3.

    Args:
        payload: ReportGenerateRequest с параметрами отчета (format: "excel"|"pdf")
        background_tasks: FastAPI BackgroundTasks для асинхронной генерации
        db: AsyncSession для сохранения записи отчета
        current_user: Текущий авторизованный пользователь

    Returns:
        ReportGenerateResponse с report_id, status="processing", estimated_time=30s

    Запускает background task generate_report_s3 и сразу возвращает 202 Accepted.
    """
    report_id = f"report-{uuid.uuid4().hex[:8]}"

    if payload.format == "excel":
        report = Report(url=f"{settings.VK_S3_ENDPOINT_URL}/{report_id}.xslx",
                        name=f"{report_id}.xlsx",
                        user_id=current_user["user_id"])
        background_tasks.add_task(
            generate_report_s3,
            "excel",
            report_id,
            payload,
            db
        )
    else:
        report = Report(url=f"{settings.VK_S3_ENDPOINT_URL}/{report_id}.pdf",
                        name=f"{report_id}.pdf",
                        user_id=current_user["user_id"])
        background_tasks.add_task(
            generate_report_s3,
            "pdf",
            report_id,
            payload,
            db
        )
    db.add(report)
    await db.commit()
    return ReportGenerateResponse(
        report_id=report_id,
        status="processing",
        estimated_time=30,
        download_url=None
    )


@router.get("/{report_id}")
async def get_report_status(report_id: str, current_user: Annotated[dict, Depends(get_current_user)]):
    """
    Перенаправляет на скачивание отчета (307 Temporary Redirect).

    Используется как промежуточный эндпоинт для проверки статуса и редиректа.

    Args:
        report_id: Уникальный ID отчета (report-abc123)
        current_user: Текущий авторизованный пользователь

    Returns:
        RedirectResponse на /reports/{report_id}/download
    """
    return RedirectResponse(url=f"/reports/{report_id}/download", status_code=307)


@router.get("/{report_id}/download")
async def download_report(report_id: str, current_user: Annotated[dict, Depends(get_current_user)]):
    """
    Генерирует signed URL для скачивания отчета из VK Cloud S3 (24 часа).

    Args:
        report_id: Уникальный ID отчета (report-abc123)
        current_user: Текущий авторизованный пользователь

    Returns:
        RedirectResponse на presigned S3 URL для прямого скачивания

    Raises:
        HTTPException:
            404: Report not ready or not found (NoSuchKey)
            403: Access denied
            500: S3 configuration error или другие ошибки
    """
    # TODO: С3 ключ адаптировать для PDF
    s3_key = f"{report_id}.xlsx"
    try:
        async with aioboto3.Session().client(
                's3',
                endpoint_url=settings.VK_S3_ENDPOINT_URL,
                aws_access_key_id=settings.VK_S3_ACCESS_KEY_ID,
                aws_secret_access_key=settings.VK_S3_SECRET_KEY
        ) as s3:
            # Проверяем существование файла
            await s3.head_object(Bucket=settings.VK_S3_REPORTS_BUCKET_NAME, Key=s3_key)

            # Генерируем signed URL (24ч)
            signed_url = await s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': settings.VK_S3_REPORTS_BUCKET_NAME, 'Key': s3_key},
                ExpiresIn=86400  # 24 часа
            )
            print(f"Signed URL generated for {report_id}: {signed_url[:50]}...")
            return RedirectResponse(url=signed_url)

    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':  # NoSuchKey
            print(f"Report {report_id} not found in S3")
            raise HTTPException(status_code=404, detail="Report not ready or not found")
        elif error_code == '403':  # AccessDenied
            print(f"Access denied for report {report_id}")
            raise HTTPException(status_code=403, detail="Access denied")
        else:
            print(f"S3 ClientError for {report_id}: {error_code}")
            raise HTTPException(status_code=500, detail="S3 error")

    except NoCredentialsError:
        print("S3 credentials not found")
        raise HTTPException(status_code=500, detail="S3 configuration error")

    except Exception as e:
        print(f"Unexpected error for report {report_id}: {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
