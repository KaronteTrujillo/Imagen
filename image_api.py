from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from lib.image_generator_lib import FreeImageGenerator, validate_prompt as validate_image_prompt
from lib.text_generator_lib import TextGenerator, validate_prompt as validate_text_prompt

# Modelos de datos
class ImageRequest(BaseModel):
    prompt: str
    service: Optional[str] = "auto"

class TextRequest(BaseModel):
    prompt: str
    personality: Optional[str] = "krampus"  # Por defecto Krampus

# Instancia de FastAPI
app = FastAPI()

# Instancias de generadores
image_generator = FreeImageGenerator()
text_generator = TextGenerator()

# Endpoint para generar imágenes
@app.post("/generate_image")
async def generate_image(request: ImageRequest):
    result = image_generator.generate_image(request.prompt, request.service)
    if not result['success']:
        raise HTTPException(status_code=400, detail=result['error'])
    return result

# Endpoint para preguntas
@app.post("/ask")
async def ask_question(request: TextRequest):
    result = text_generator.generate_with_llama3(request.prompt, request.personality)
    if not result['success']:
        raise HTTPException(status_code=400, detail=result['error'])
    return result
