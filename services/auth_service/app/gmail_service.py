import base64
import os

from email.message import EmailMessage
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


SCOPES = [
    "https://www.googleapis.com/auth/gmail.send"
]

AUTH_SERVICE_DIR = Path(__file__).resolve().parent.parent

CREDENTIALS_PATH = (
    AUTH_SERVICE_DIR / "credentials.json"
)

TOKEN_PATH = (
    AUTH_SERVICE_DIR / "token.json"
)


def get_gmail_credentials():
    credentials = None

    if TOKEN_PATH.exists():
        credentials = Credentials.from_authorized_user_file(
            str(TOKEN_PATH),
            SCOPES
        )

    if not credentials or not credentials.valid:
        if (
            credentials
            and credentials.expired
            and credentials.refresh_token
        ):
            credentials.refresh(Request())

        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_PATH),
                SCOPES
            )

            credentials = flow.run_local_server(port=0)

        TOKEN_PATH.write_text(
            credentials.to_json(),
            encoding="utf-8"
        )

    return credentials


def send_password_reset_email(
    destinatario,
    nome,
    codigo
    ):
    remetente = os.getenv("GMAIL_SENDER")

    if not remetente:
        raise ValueError(
            "GMAIL_SENDER não foi configurado."
        )

    credentials = get_gmail_credentials()

    gmail = build(
        "gmail",
        "v1",
        credentials=credentials,
        cache_discovery=False
    )

    mensagem = EmailMessage()

    mensagem["To"] = destinatario
    mensagem["From"] = remetente
    mensagem["Subject"] = (
        "Código de recuperação — Senac Tech"
    )

    mensagem.set_content(
        f"""
    Olá, {nome}.

    Seu código para redefinir a senha é:

    {codigo}

    Esse código expira em 15 minutos.

    Se você não solicitou a recuperação, ignore este e-mail.

    Senac Tech
    """.strip()
    )

    mensagem_codificada = base64.urlsafe_b64encode(
        mensagem.as_bytes()
    ).decode("utf-8")

    gmail.users().messages().send(
        userId="me",
        body={
            "raw": mensagem_codificada
        }
    ).execute()