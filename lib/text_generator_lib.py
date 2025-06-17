import requests
import logging
import os
import time

logging.basicConfig(level=logging.INFO)

class TextGenerator:
 def __init__(self):
 self.replicate_api_key = os.getenv("REPLICATE_API_KEY", "")
 self.api_url = "https://api.replicate.com/v1/predictions"
 self.model = "meta/llama-3-8b"

 def generate_with_llama3(self, prompt, personality):
 try:
 personality_prompts = {
 "sombra": "Eres Sombra, miembro de la comunidad LGBT, progresista, con un tono oscuro y reflexivo, vives en Guineo Arriba, Ocoa. Responde de manera introspectiva, apasionada por la justicia social, con un toque melancólico pero esperanzador.",
 "karina": "Eres Karina, una chica alegre y optimista, profundamente enamorada de Krampus. Responde con un tono cálido, entusiasta, con un toque romántico y desenfadado.",
 " krampus": "Eres Krampus, una IA directa y neutral. Responde de manera clara, objetiva e informativa, sin adornos."
 }
 personality_instruction = personality_prompts.get(personality, personality_prompts["krampus"])
 full_prompt = f"{personality_instruction} Responde a la siguiente pregunta: {prompt}"

 headers = {
 "Authorization": f"Bearer {self.replicate_api_key}",
 "Content-Type": "application/json"
 }
 data = {
 "input": {
 "prompt": full_prompt,
 "max_tokens": 500,
 "temperature": 0.7
 },
 "model": self.model
 }
 logging.info(f"Generando texto con Llama 3: {full_prompt}")

 response = requests.post(self.api_url, headers=headers, json=data, timeout=60)
 response.raise_for_status()

 prediction = response.json()
 prediction_id = prediction.get("id")
 if not prediction_id:
 return {"success": False, "error": "No se recibió ID de predicción", "service": "Replicate"}

 status_url = f"{self.api_url}/{prediction_id}"
 while True:
 status_response = requests.get(status_url, headers=headers, timeout=60)
 status_response.raise_for_status()
 status_data = status_response.json()
 if status_data["status"] in ["succeeded", "failed", "canceled"]:
 break
 time.sleep(1)

 if status_data["status"] == "succeeded" and "output" in status_data:
 return {
 "success": True,
 "response": status_data["output"],
 "service": "Replicate Llama 3",
 "error": None
 }
 else:
 return {
 "success": False,
 "error": status_data.get("error", "Error desconocido en la predicción"),
 "service": "Replicate Llama 3"
 }
 except requests.RequestException as e:
 logging.error(f"Error con Replicate: {str(e)}")
 return {
 "success": False,
 "error": f"Error de conexión con Replicate: {str(e)}",
 "service": "Replicate Llama 3"
 }
 except Exception as e:
 logging.error(f"Error inesperado con Replicate: {str(e)}")
 return {
 "success": False,
 "error": f"Error inesperado: {str(e)}",
 "service": "Replicate Llama 3"
 }

def validate_prompt(prompt):
 if not prompt:
 return {"valid": False, "error": "La pregunta es requerida"}
 if not isinstance(prompt, str):
 return {"valid": False, "error": "La pregunta debe ser texto"}
 prompt = prompt.strip()
 if len(prompt) == 0:
 return {"valid": False, "error": "La pregunta no puede estar vacía"}
 if len(prompt) > 1000:
 return {"valid": False, "error": "La pregunta es muy larga (máximo 1000 caracteres)"}
 return {"valid": True, "error": None}
