from fastapi import APIRouter, FastAPI, Request
from schemas.mcp import *
import subprocess

mcp_router = APIRouter()

