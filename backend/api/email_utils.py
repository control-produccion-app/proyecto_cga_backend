from django.core.mail import send_mail
from django.conf import settings


def enviar_codigo_2fa(email, codigo, username):
    mensaje = (
        f"Hola {username},\n\n"
        f"Tu código de verificación para acceder al sistema es:\n\n"
        f"{codigo}\n\n"
        f"Este código expira en {settings.TWO_FACTOR_CODE_EXPIRY_MINUTES} minutos.\n\n"
        f"Si no solicitaste este acceso, ignora este mensaje.\n"
    )
    send_mail(
        subject='Código de verificación - Control de Producción',
        message=mensaje,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )
