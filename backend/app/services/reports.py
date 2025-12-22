import os
import tempfile
from asyncio import to_thread
from pathlib import Path

import aioboto3
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.fonts import addMapping
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.config import settings
from backend.app.core.logging_config import get_logger
from backend.app.models import CattleDetection
from backend.schemas.reports import ReportGenerateRequest

logger = get_logger(__name__)

TEMP_DIR = Path(tempfile.gettempdir()) / "reports"
TEMP_DIR.mkdir(exist_ok=True)


def _generate_pdf_report(local_path: Path, df: pd.DataFrame, payload):
    """
    Генерирует PDF отчет с помощью ReportLab (выполняется в отдельном потоке).

    Args:
        local_path: Путь к выходному PDF файлу
        df: pandas DataFrame с данными взвешиваний
        payload: ReportGenerateRequest с типом отчета (summary/detailed)

    Примечание:
        Создает таблицу взвешиваний + сводку по животным (если report_type="summary")
        Использует A4 формат, стили ReportLab (grey header, beige rows)
    """
    # TODO: добавить дату генерации
    # TODO: добавить логин сгенерировавшего отчёт юзера
    # TODO: улучшить общую структуру отчёта, сделать более приятным глазу, убрать поле nn_animal_id
    doc = SimpleDocTemplate(str(local_path), pagesize=A4)
    story = []
    styles = getSampleStyleSheet()
    
    # Создаём стиль для заголовка с явным указанием шрифта
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontName='Helvetica-Bold',
        fontSize=16,
        textColor=colors.black,
        spaceAfter=12,
    )
    story.append(Paragraph("Weighings Report", title_style))
    story.append(Spacer(1, 12))
    if not df.empty:
        table_data = [df.columns.tolist()] + df.values.tolist()
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(table)
    # Свод
    if payload.report_type == "summary":
        summary = df.groupby('animal_id')['weight'].agg(['count', 'mean']).round(2)
        summary.columns = ['Quantity', 'Mean Weight']
        story.append(Spacer(1, 20))
        story.append(Paragraph("Animal Summary", styles['Heading2']))
        summary_data = [summary.columns.tolist()] + summary.values.tolist()
        summary_table = Table(summary_data)
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(summary_table)
    doc.build(story)


async def generate_report_s3(mode: str, report_id: str, payload: ReportGenerateRequest, db: AsyncSession):
    """
    Асинхронно генерирует Excel/PDF отчет и загружает в VK Cloud S3 Storage.

    Args:
        mode: "excel" или "pdf" формат отчета
        report_id: Уникальный ID отчета (report-abc123)
        payload: ReportGenerateRequest с фильтрами (dates, animal_ids, include_weighs)
        db: AsyncSession для запроса CattleDetection данных

    Фильтры запроса:
        - start_date/end_date: диапазон дат
        - animal_ids: список номеров бирок
        - include_weighs: список CattleDetection.id

    Raises:
        Exception: Любые ошибки логируются и перебрасываются для background task
    """
    local_path = TEMP_DIR / f"{report_id}.{'pdf' if mode == 'pdf' else 'xlsx'}"
    s3_key = f"{report_id}.{'pdf' if mode == 'pdf' else 'xlsx'}"
    content_type = 'application/pdf' if mode == 'pdf' else 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

    logger.info(f"Starting report generation: {report_id} (mode: {mode})")
    try:
        query = select(CattleDetection)
        if payload.start_date:
            query = query.where(CattleDetection.create_datetime >= payload.start_date)
        if payload.end_date:
            query = query.where(CattleDetection.create_datetime <= payload.end_date)
        if payload.animal_ids:
            query = query.where(CattleDetection.animal_id.in_(payload.animal_ids))
        if payload.include_weighs:
            query = query.where(CattleDetection.id.in_(payload.include_weighs))

        result = await db.execute(query)
        detections = result.scalars().all()
        logger.debug(f"Found {len(detections)} detections for report {report_id}")
        data = [{
            "animal_id": d.animal_id,
            "weight": d.weight,
            "confidence": d.confidence,
            "datetime": d.create_datetime.isoformat() if d.create_datetime else None,
            "image_id": d.image_id,
            "nn_object_id": d.nn_object_id
        } for d in detections]
        df = pd.DataFrame(data)

        if mode == 'excel':
            # Excel генерация (оригинальная логика)
            logger.debug(f"Generating Excel report: {report_id}")
            with pd.ExcelWriter(local_path, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Взвешивания')

                if payload.report_type == "summary" and not df.empty:
                    summary = df.groupby('animal_id')['weight'].agg(['count', 'mean']).round(2)
                    summary.to_excel(writer, sheet_name='Сводка')

        elif mode == 'pdf':
            logger.debug(f"Generating PDF report: {report_id}")
            await to_thread(_generate_pdf_report, local_path, df, payload)
        
        logger.debug(f"Report file generated locally: {local_path}")

        logger.debug(f"Uploading report to S3: {s3_key}")
        async with aioboto3.Session().client(
                's3',
                endpoint_url=settings.VK_S3_ENDPOINT_URL,
                aws_access_key_id=settings.VK_S3_ACCESS_KEY_ID,
                aws_secret_access_key=settings.VK_S3_SECRET_KEY,
                region_name=settings.VK_S3_REGION
        ) as s3:
            await s3.upload_file(
                str(local_path),
                settings.VK_S3_REPORTS_BUCKET_NAME,
                s3_key,
                ExtraArgs={'ContentType': content_type}
            )

        logger.info(f"Report {report_id} ({mode.upper()}) uploaded to s3://{settings.VK_S3_REPORTS_BUCKET_NAME}/{s3_key}")

    except Exception as e:
        logger.exception(f"Report {report_id} ({mode}) generation failed: {e}")
        raise  # Перебрасываем ошибку для логирования в background task
    finally:
        # Очищаем локальный файл
        if local_path.exists():
            local_path.unlink()
