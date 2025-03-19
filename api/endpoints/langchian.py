from fastapi import APIRouter, File, UploadFile, Form
from fastapi.responses import JSONResponse
from schemas.langchain import *
from fastapi import FastAPI, Request


langchain_router = APIRouter()

@langchain_router.post("/UploadFile/")
async def upload_file(request:Request):
    request_data = await request.json()
    return {"message": "Request received"}
