import logging

from django.conf import settings

logger = logging.getLogger(__name__)


def enviar_codigo_2fa(email, codigo, username):
    try:
        import sib_api_v3_sdk
        from sib_api_v3_sdk.rest import ApiException

        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = settings.BREVO_API_KEY

        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
            sib_api_v3_sdk.ApiClient(configuration)
        )

        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=[{"email": email, "name": username}],
            sender={
                "email": settings.DEFAULT_FROM_EMAIL,
                "name": "Control de Producción",
            },
            subject="Código de verificación - Control de Producción",
            text_content=(
                f"Hola {username},\n\n"
                f"Tu código de verificación para acceder al sistema es:\n\n"
                f"{codigo}\n\n"
                f"Este código expira en {settings.TWO_FACTOR_CODE_EXPIRY_MINUTES} minutos.\n\n"
                f"Si no solicitaste este acceso, ignora este mensaje."
            ),
        )

        api_instance.send_transac_email(send_smtp_email)
        logger.info(f"Código 2FA enviado a {email}")

    except ImportError:
        logger.error(
            "sib-api-v3-sdk no está instalado. "
            "Ejecuta: pip install sib-api-v3-sdk"
        )
    except ApiException as e:
        logger.error(f"Error de API Brevo al enviar email a {email}: {e}")
    except Exception as e:
        logger.error(f"Error inesperado al enviar email a {email}: {e}")
