import requests
import logging
import time
import base64
import os

# Configuración de logging
logging.basicConfig(level=logging.INFO)

class FreeImageGenerator:
    def __init__(self):
        # Cargar la clave API de Hugging Face desde variable de entorno
        self.hf_api_key = os.getenv("HUGGINGFACE_API_KEY", "")
        self.services = [
            {
                'name': 'Pollinations',
                'url': 'https://image.pollinations.ai/prompt/{prompt}',
                'method': 'GET',
                'free': True,
                'unlimited': True
            },
            {
                'name': 'Hugging Face Stable Diffusion',
                'url': 'https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1',
                'method': 'POST',
                'free': True,
                'rate_limited': True
            }
        ]

    def generate_with_pollinations(self, prompt):
        try:
            clean_prompt = prompt.replace(' ', '%20').replace(',', '%2C')
            url = f"https://image.pollinations.ai/prompt/{clean_prompt}"
            params = {
                'width': '1024',
                'height': '1024',
                'seed': str(int(time.time())),
                'model': 'flux'
            }
            param_string = '&'.join([f"{k}={v}" for k, v in params.items()])
            full_url = f"{url}?{param_string}"
            logging.info(f"Generando imagen con Pollinations: {full_url}")

            response = requests.get(full_url, timeout=60)
            response.raise_for_status()

            if response.headers.get('content-type', '').startswith('image/'):
                image_base64 = base64.b64encode(response.content).decode('utf-8')
                return {
                    'success': True,
                    'image_base64': image_base64,
                    'image_url': full_url,
                    'service': 'Pollinations AI',
                    'error': None
                }
            else:
                return {
                    'success': False,
                    'error': 'La respuesta no es una imagen válida',
                    'service': 'Pollinations AI'
                }
        except requests.RequestException as e:
            logging.error(f"Error con Pollinations: {str(e)}")
            return {
                'success': False,
                'error': f'Error de conexión con Pollinations: {str(e)}',
                'service': 'Pollinations AI'
            }
        except Exception as e:
            logging.error(f"Error inesperado con Pollinations: {str(e)}")
            return {
                'success': False,
                'error': f'Error inesperado: {str(e)}',
                'service': 'Pollinations AI'
            }

    def generate_with_huggingface(self, prompt):
        try:
            url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.hf_api_key}"
            }
            data = {
                "inputs": prompt,
                "parameters": {
                    "num_inference_steps": 20,
                    "guidance_scale": 7.5,
                    "width": 768,
                    "height": 768
                }
            }
            logging.info(f"Generando imagen con Hugging Face: {prompt}")

            response = requests.post(url, headers=headers, json=data, timeout=60)
            if response.status_code == 503:
                return {
                    'success': False,
                    'error': 'El modelo se está cargando, intenta de nuevo en unos momentos',
                    'service': 'Hugging Face'
                }
            response.raise_for_status()

            image_base64 = base64.b64encode(response.content).decode('utf-8')
            return {
                'success': True,
                'image_base64': image_base64,
                'image_url': None,
                'service': 'Hugging Face Stable Diffusion',
                'error': None
            }
        except requests.RequestException as e:
            logging.error(f"Error con Hugging Face: {str(e)}")
            return {
                'success': False,
                'error': f'Error de conexión con Hugging Face: {str(e)}',
                'service': 'Hugging Face'
            }
        except Exception as e:
            logging.error(f"Error inesperado con Hugging Face: {str(e)}")
            return {
                'success': False,
                'error': f'Error inesperado: {str(e)}',
                'service': 'Hugging Face'
            }

    def generate_image(self, prompt, preferred_service='pollinations'):
        validation = validate_prompt(prompt)
        if not validation['valid']:
            return validation

        if preferred_service == 'pollinations' or preferred_service == 'auto':
            result = self.generate_with_pollinations(prompt)
            if result['success']:
                return result

        if preferred_service == 'huggingface' or preferred_service == 'auto':
            if not self.hf_api_key:
                return {
                    'success': False,
                    'error': 'Se requiere una clave API para Hugging Face',
                    'service': 'Hugging Face'
                }
            result = self.generate_with_huggingface(prompt)
            if result['success']:
                return result

        return {
            'success': False,
            'error': 'Todos los servicios gratuitos están temporalmente no disponibles.',
            'service': 'Ninguno disponible'
        }

def validate_prompt(prompt):
    if not prompt:
        return {"valid": False, "error": "La descripción es requerida"}
    if not isinstance(prompt, str):
        return {"valid": False, "error": "La descripción debe ser texto"}
    prompt = prompt.strip()
    if len(prompt) == 0:
        return {"valid": False, "error": "La descripción no puede estar vacía"}
    if len(prompt) > 1000:
        return {"valid": False, "error": "La descripción es muy larga (máximo 1000 caracteres)"}
    return {"valid": True, "error": None}
