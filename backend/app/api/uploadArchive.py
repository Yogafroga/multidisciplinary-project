import uuid
from typing import List
from fastapi import APIRouter, UploadFile, File, status, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(tags=['Upload'])

@router.post("upload_archive", status_code=status.HTTP_201_CREATED)
async def upload_archive(    
  file: UploadFile = File(...),
  session: AsyncSession = Depends(get_db),
  current_user: dict = Depends(get_current_user)
  ):
  