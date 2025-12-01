import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from os import environ

SMTP_SERVER = environ.get('SMTP_SERVER')
SMTP_PORT = int(environ.get('SMTP_PORT'))
SENDER_EMAIL = environ.get('SENDER_EMAIL')
SENDER_PASSWORD = environ.get('SENDER_PASSWORD')
RECEIVER_EMAIL = environ.get('RECEIVER_EMAIL')

PRIMARY_COLOR = '#4361ee'
BODY_BG_COLOR = '#f9fbfd'
CARD_BG_COLOR = '#ffffff'
LOGO_TEXT = '2Work Transport Solutions'


def create_email_html(data):
    rating_stars = ''.join([
        '<span style="color: gold; font-size: 1.2em;">&#9733;</span>'
        for _ in range(data['rating'])
    ])

    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Nueva Consulta de Contacto</title>
        <style>
            /* Estilos generales para email marketing */
            body, table, td, a {{ -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; }}
            table, td {{ border-collapse: collapse; }}
        </style>
    </head>
    <body style="margin: 0; padding: 0; background-color: {BODY_BG_COLOR}; font-family: Arial, sans-serif; line-height: 1.6; color: #333333;">

        <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: {BODY_BG_COLOR};">
            <tr>
                <td align="center" style="padding: 30px 10px;">
                    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px;">

                        <tr>
                            <td align="center" style="background-color: {PRIMARY_COLOR}; padding: 20px; border-radius: 8px 8px 0 0; color: white; font-size: 24px; font-weight: bold;">
                                {LOGO_TEXT} - Nueva Consulta
                            </td>
                        </tr>

                        <tr>
                            <td align="left" style="background-color: {CARD_BG_COLOR}; padding: 20px; border-radius: 0 0 8px 8px; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);">
                                <h1 style="font-size: 20px; margin-top: 0; border-bottom: 2px solid {PRIMARY_COLOR}; padding-bottom: 10px; color: #333333;">
                                    Detalles de la Consulta
                                </h1>

                                <p style="font-weight: bold; color: #555555; margin-top: 15px; margin-bottom: 5px;">Nombre del Usuario:</p>
                                <p style="color: #333333; font-size: 16px; margin: 0 0 15px 0;">{data['name']}</p>

                                <p style="font-weight: bold; color: #555555; margin-top: 15px; margin-bottom: 5px;">Correo Electrónico:</p>
                                <p style="font-size: 16px; margin: 0 0 15px 0;">
                                    <a href="mailto:{data['email']}" style="color: {PRIMARY_COLOR}; text-decoration: none;">{data['email']}</a>
                                </p>

                                <p style="font-weight: bold; color: #555555; margin-top: 15px; margin-bottom: 5px;">Asunto:</p>
                                <p style="color: #333333; font-size: 16px; margin: 0 0 15px 0;">{data['subject']}</p>

                                <p style="font-weight: bold; color: #555555; margin-top: 15px; margin-bottom: 5px;">Evaluación de Experiencia:</p>
                                <p style="font-size: 16px; margin: 0 0 20px 0;">
                                    {rating_stars}
                                    <span style="color: #333333;"> ({data['rating']} / 5)</span>
                                </p>

                                <h2 style="font-size: 18px; color: {PRIMARY_COLOR}; margin-top: 25px; margin-bottom: 5px;">Mensaje Completo:</h2>
                                <div style="border: 1px solid #eeeeee; padding: 15px; border-radius: 4px; background-color: #f7f7f7;">
                                    <p style="white-space: pre-wrap; margin: 0; font-size: 15px;">{data['message']}</p>
                                </div>
                            </td>
                        </tr>

                        <tr>
                            <td align="center" style="padding-top: 20px;">
                                <p style="font-size: 12px; color: #aaaaaa; margin: 0;">
                                    Este correo fue enviado automáticamente desde el formulario de contacto de {LOGO_TEXT}.
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    return html_content


def send_contact_email(data):
    """Envía el correo de contacto usando los datos recibidos del formulario, con formato HTML."""

    plain_text_body = f"""
    --- Nueva Consulta de {LOGO_TEXT} ---

    Asunto: {data['subject']}

    Nombre: {data['name']}
    Correo: {data['email']}
    Calificación del Sitio: {data['rating']} / 5 estrellas

    --- Mensaje ---
    {data['message']}
    """

    html_body = create_email_html(data)

    message = MIMEMultipart('alternative')
    message['Subject'] = f"Consulta de {LOGO_TEXT}: {data['subject']}"
    message['From'] = SENDER_EMAIL
    message['To'] = RECEIVER_EMAIL

    message.attach(MIMEText(plain_text_body, 'plain'))
    message.attach(MIMEText(html_body, 'html'))

    try:
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, message.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"ERROR al enviar correo (SMTP): {e}")
        return False