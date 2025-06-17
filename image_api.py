from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from lib.image_generator_lib import FreeImageGenerator, validate_prompt

# Modelo de datos para la solicitud del bot
class ImageRequest(BaseModel):
    prompt: str
    service: Optional[str] = "auto"

# Instancia de FastAPI
app = FastAPI()

# Instancia del generador
free_generator = FreeImageGenerator()

# Endpoint para generar imágenes
@app.post("/generate_image")
async def generate_image(request: ImageRequest):
    result = free_generator.generate_image(request.prompt, request.service)
    if not result['success']:
        raise HTTPException(status_code=400, detail=result['error'])
    return result
