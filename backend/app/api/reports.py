import uuid
import logging
from typing import Annotated

import aioboto3
from pathlib import Path

from botocore.exceptions import ClientError, NoCredentialsError
from fastapi import APIRouter, status, HTTPException, BackgroundTasks, Depends
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from io import BytesIO

from backend.app.models import Report
from backend.schemas.reports import ReportGenerateRequest, ReportGenerateResponse
from backend.app.services.auth import db_dependency, get_current_user
from backend.app.core.config import settings
from backend.app.core.logging_config import get_logger
from backend.app.services.reports import generate_report_s3
import tempfile

logger = get_logger(__name__)

router = APIRouter(prefix="/reports", tags=["reports"])
TEMP_DIR = Path(tempfile.gettempdir()) / "reports"
TEMP_DIR.mkdir(exist_ok=True)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


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
        user_id = int(current_user["user_id"])
        logger.debug(f"Fetching reports for user {user_id}")
        query = select(Report).where(Report.user_id == user_id)
        result = await db.execute(query)
        reports = result.scalars().all()
        reports_data = [{
            "id": report.id,
            "name": report.name,
            "url": report.url
        } for report in reports]

        logger.info(f"Retrieved {len(reports_data)} reports for user {user_id}")
        return {
            "user_id": user_id,
            "reports": reports_data
        }
    except NoCredentialsError:
        logger.warning(f"No credentials provided for user reports request")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No credentials provided",
        )
    except Exception as e:
        logger.exception(f"Database error while fetching user reports: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}",
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
    user_id = current_user["user_id"]
    logger.info(f"Starting report generation: {report_id} (format: {payload.format}, user: {user_id})")

    if payload.format == "excel":
        report = Report(url=f"{settings.VK_S3_ENDPOINT_URL}/{report_id}.xslx",
                        name=f"{report_id}.xlsx",
                        user_id=user_id)
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
                        user_id=user_id)
        background_tasks.add_task(
            generate_report_s3,
            "pdf",
            report_id,
            payload,
            db
        )
    db.add(report)
    await db.commit()
    logger.info(f"Report {report_id} queued for generation")
    return ReportGenerateResponse(
        report_id=report_id,
        status="processing",
        estimated_time=30,
        download_url=None
    )


@router.get("/{report_id}/download")
async def download_report(
        report_id: str,
        current_user: Annotated[dict, Depends(get_current_user)],
        db: db_dependency,
):
    """
    Генерирует signed URL для скачивания отчета из VK Cloud S3 (24 часа).

    Args:
        report_id: ID отчета report-{uuid[:8]} (report-abc123)
        current_user: Текущий авторизованный пользователь
        db: AsyncSession для проверки отчета

    Returns:
        RedirectResponse на presigned S3 URL для прямого скачивания

    Raises:
        HTTPException:
            404: Report not ready or not found
            403: Access denied (чужой отчет)
            500: S3 configuration error
    """
    # Ищем отчет по паттерну: report-abc123 → report-abc123*.xlsx/pdf
    user_id = current_user["user_id"]
    logger.info(f"Download request for report {report_id} by user {user_id}")
    report_pattern = f"{report_id}%"
    report_query = select(Report).where(
        Report.name.like(report_pattern),  # report-abc123.xlsx/pdf
        Report.user_id == user_id
    )
    result = await db.execute(report_query)
    report = result.scalar_one_or_none()

    if not report:
        logger.warning(f"Report {report_id} not found or access denied for user {user_id}")
        raise HTTPException(status_code=403, detail="Report not found or access denied")

    if not report.url:
        logger.warning(f"Report {report_id} not ready yet (no URL)")
        raise HTTPException(status_code=404, detail="Report not ready")

    s3_key = report.name  # Полное имя из БД: report-abc123.xlsx

    try:
        logger.info(f"Attempting S3 access: bucket={settings.VK_S3_REPORTS_BUCKET_NAME}, key={s3_key}, endpoint={settings.VK_S3_ENDPOINT_URL}, region={settings.VK_S3_REGION}")
        async with aioboto3.Session().client(
                's3',
                endpoint_url=settings.VK_S3_ENDPOINT_URL,
                aws_access_key_id=settings.VK_S3_ACCESS_KEY_ID,
                aws_secret_access_key=settings.VK_S3_SECRET_KEY,
                region_name=settings.VK_S3_REGION
        ) as s3:
            logger.debug(f"Checking if object exists: {s3_key}")
            await s3.head_object(Bucket=settings.VK_S3_REPORTS_BUCKET_NAME, Key=s3_key)
            logger.debug(f"Object exists, generating download URL")

            signed_url = await s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': settings.VK_S3_REPORTS_BUCKET_NAME, 'Key': s3_key},
                ExpiresIn=86400
            )
            logger.info(f"Signed URL generated for {report_id} → {s3_key} (user {current_user['user_id']})")
            
            # Получаем файл из S3
            response = await s3.get_object(Bucket=settings.VK_S3_REPORTS_BUCKET_NAME, Key=s3_key)
            file_content = await response['Body'].read()
            
            # Определяем Content-Type по расширению файла
            content_type = ("application/vnd.openxmlformats"
                            "-officedocument.spreadsheetml.sheet") if s3_key.endswith('.xlsx') else "application/pdf"
            
            # Возвращаем файл как поток
            return StreamingResponse(
                BytesIO(file_content),
                media_type=content_type,
                headers={
                    "Content-Disposition": f"attachment; filename={s3_key}",
                }
            )

    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'NoSuchKey':
            logger.warning(f"Report file not found in S3: {report_id} ({s3_key})")
            raise HTTPException(status_code=404, detail="Report file not found in storage")
        elif error_code == 'AccessDenied':
            logger.error(f"S3 access denied for report {report_id} ({s3_key})")
            raise HTTPException(status_code=403, detail="Storage access denied")
        else:
            logger.error(f"S3 error for report {report_id}: {error_code}")
            raise HTTPException(status_code=500, detail="Storage error")

    except Exception as e:
        logger.exception(f"Unexpected error downloading report {report_id}: {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
