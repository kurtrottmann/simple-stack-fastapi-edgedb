import logging
from pathlib import Path
from typing import Any, Dict, List
from uuid import UUID

import emails
from emails.template import JinjaTemplate
from fastapi import HTTPException
from pydantic import EmailStr

from .config import settings

ALGORITHM = "HS256"


def send_email(
    email_to: str,
    subject_template: str = "",
    html_template: str = "",
    environment: Dict[str, Any] = {},
) -> None:
    assert settings.EMAILS_ENABLED, "no provided configuration for email variables"
    message = emails.Message(
        subject=JinjaTemplate(subject_template),
        html=JinjaTemplate(html_template),
        mail_from=(settings.EMAILS_FROM_NAME, settings.EMAILS_FROM_EMAIL),
    )
    smtp_options = {"host": settings.SMTP_HOST, "port": settings.SMTP_PORT}
    if settings.SMTP_TLS:
        smtp_options["tls"] = True
    if settings.SMTP_USER:
        smtp_options["user"] = settings.SMTP_USER
    if settings.SMTP_PASSWORD:
        smtp_options["password"] = settings.SMTP_PASSWORD
    response = message.send(to=email_to, render=environment, smtp=smtp_options)
    logging.info(f"send email result: {response}")


def send_test_email(email_to: str) -> None:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Test email"
    with open(Path(settings.EMAIL_TEMPLATES_DIR) / "test_email.html") as f:
        template_str = f.read()
    send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={"project_name": settings.PROJECT_NAME, "email": email_to},
    )


def send_reset_password_email(email_to: EmailStr, email: str, token: str) -> None:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Password recovery for user {email}"
    with open(Path(settings.EMAIL_TEMPLATES_DIR) / "reset_password.html") as f:
        template_str = f.read()
    server_host = settings.EMAILS_SERVER_HOST
    link = f"{server_host}/reset-password?token={token}"
    send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={
            "project_name": settings.PROJECT_NAME,
            "username": email,
            "email": email_to,
            "valid_hours": settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS,
            "link": link,
        },
    )


def send_new_account_email(email_to: str, username: str, password: str) -> None:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - New account for user {username}"
    with open(Path(settings.EMAIL_TEMPLATES_DIR) / "new_account.html") as f:
        template_str = f.read()
    link = settings.EMAILS_SERVER_HOST
    send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={
            "project_name": settings.PROJECT_NAME,
            "username": username,
            "password": password,
            "email": email_to,
            "link": link,
        },
    )


def get_type(value: Any) -> str:
    if type(value) == bool:
        return "<bool>"
    elif type(value) == str:
        return "<str>"
    elif type(value) == int:
        return "<int64>"
    elif type(value) == UUID:
        return "<uuid>"
    else:
        raise ValueError("Type not found.")


def get_shape(data: Dict[str, Any]) -> str:
    shape_list = [f"{k} := {get_type(v)}${k}" for k, v in data.items()]
    shape_expr = ", ".join(shape_list)
    return shape_expr


def get_filter(filtering: Dict[str, Any]) -> str:
    filter_list = [
        f".{f.replace('__','.')} = {get_type(v)}${f}" for f, v in filtering.items()
    ]
    filter_expr = " AND ".join(filter_list)
    return filter_expr


def get_order(ordering: str, ordering_fields: List) -> str:
    order_list = []
    fields = ordering.split(",")
    for f in fields:
        if f.startswith("-"):
            f = f[1:]
            direction = " DESC"
        else:
            direction = ""
        if f in ordering_fields:
            order_list.append(f".{f.replace('__','.')}{direction}")
        else:
            raise HTTPException(
                status_code=400, detail=f"Ordering field '{f}' not allowed."
            )
    order_expr = " THEN ".join(order_list)
    return order_expr
