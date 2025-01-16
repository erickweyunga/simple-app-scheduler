import requests
from app.config import Config
from app.utils.logger import setup_logger

logger = setup_logger()


def send_whatsapp_message(phone_number, message_data, auth_token, phone_number_id):
    try:
        url = f"{Config.WHATSAPP_API_URL}/{Config.WHATSAPP_API_VERSION}/{phone_number_id}/messages"

        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json",
        }

        payload = {"messaging_product": "whatsapp", "to": phone_number, **message_data}

        logger.info(f"Sending WhatsApp message to {phone_number}")
        logger.debug(f"Request payload: {payload}")

        # Configure request timeout and retries
        timeout = (5, 15)  # (connection timeout, read timeout)
        retry_strategy = requests.adapters.Retry(
            total=3,  # total number of retries
            backoff_factor=0.5,  # wait 0.5s * (2 ** retry) between retries
            status_forcelist=[
                408,
                429,
                500,
                502,
                503,
                504,
            ],  # retry on these status codes
        )

        # Create session with retry strategy
        session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)

        try:
            response = session.post(url, json=payload, headers=headers, timeout=timeout)
            response_data = response.json()

            logger.info(f"WhatsApp API Response status: {response.status_code}")
            logger.debug(f"WhatsApp API Response: {response_data}")

            return response_data

        except requests.exceptions.ConnectTimeout:
            logger.error("Connection timeout while connecting to WhatsApp API")
            return {"error": "Connection timeout occurred"}

        except requests.exceptions.ReadTimeout:
            logger.error("Read timeout while waiting for WhatsApp API response")
            return {"error": "Read timeout occurred"}

        except requests.exceptions.ConnectionError:
            logger.error("Connection error occurred while connecting to WhatsApp API")
            return {"error": "Connection error occurred"}

        finally:
            session.close()

    except Exception as e:
        logger.error(f"Error sending WhatsApp message: {str(e)}", exc_info=True)
        return {"error": str(e)}
