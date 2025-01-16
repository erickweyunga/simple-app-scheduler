import requests
from app.config import Config
from app.utils.logger import setup_logger

logger = setup_logger()


def create_whatsapp_template(auth_token, phone_number_id, template_data):
    try:
        url = f"{Config.WHATSAPP_API_URL}/{Config.WHATSAPP_API_VERSION}/{phone_number_id}/message_templates"

        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json",
        }

        logger.info(f"Creating new WhatsApp template: {template_data.get('name')}")
        logger.debug(f"Template data: {template_data}")

        response = requests.post(url, json=template_data, headers=headers)
        response_data = response.json()

        logger.info(f"Template creation response status: {response.status_code}")
        logger.debug(f"Template creation response: {response_data}")

        return response_data

    except Exception as e:
        logger.error(f"Error creating template: {str(e)}", exc_info=True)
        return None


def get_whatsapp_templates(auth_token, phone_number_id):
    try:
        url = f"{Config.WHATSAPP_API_URL}/{Config.WHATSAPP_API_VERSION}/{phone_number_id}/message_templates"

        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json",
        }

        logger.info("Fetching WhatsApp templates")

        response = requests.get(url, headers=headers)
        response_data = response.json()

        logger.info(f"Template fetch response status: {response.status_code}")
        logger.debug(f"Templates fetched: {response_data}")

        return response_data

    except Exception as e:
        logger.error(f"Error fetching templates: {str(e)}", exc_info=True)
        return None
