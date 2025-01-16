from flask import Blueprint, request, jsonify
from app.services.template_service import (
    create_whatsapp_template,
    get_whatsapp_templates,
)
from app.utils.logger import setup_logger

logger = setup_logger()
template_blueprint = Blueprint("templates", __name__)


@template_blueprint.route("/templates", methods=["POST"])
def create_template():
    try:
        logger.info("Received template creation request")
        data = request.get_json()

        # Validate required fields
        required_fields = ["auth_token", "phone_number_id", "template"]
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            logger.error(f"Missing required fields: {missing_fields}")
            return (
                jsonify(
                    {"error": f"Missing required fields: {', '.join(missing_fields)}"}
                ),
                400,
            )

        response = create_whatsapp_template(
            auth_token=data["auth_token"],
            phone_number_id=data["phone_number_id"],
            template_data=data["template"],
        )

        if response:
            return (
                jsonify(
                    {
                        "message": "Template creation request submitted",
                        "response": response,
                    }
                ),
                201,
            )
        else:
            return jsonify({"error": "Failed to create template"}), 500

    except Exception as e:
        logger.error(f"Error in template creation: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@template_blueprint.route("/templates", methods=["GET"])
def list_templates():
    try:
        auth_token = request.headers.get("Authorization")
        phone_number_id = request.args.get("phone_number_id")

        if not auth_token or not phone_number_id:
            return (
                jsonify(
                    {
                        "error": "Missing required parameters. Please provide Authorization header and phone_number_id"
                    }
                ),
                400,
            )

        # Remove 'Bearer ' if present
        auth_token = auth_token.replace("Bearer ", "")

        templates = get_whatsapp_templates(auth_token, phone_number_id)

        if templates:
            return jsonify(templates), 200
        else:
            return jsonify({"error": "Failed to fetch templates"}), 500

    except Exception as e:
        logger.error(f"Error fetching templates: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500
