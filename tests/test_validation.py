from app.schemas.auth import SendCodeRequest, TwoFARequest
from app.schemas.instances import InstanceCreate
from app.schemas.messages import SendMessageRequest

import pytest
from pydantic import ValidationError


def test_instance_create_valid():
    InstanceCreate(name="My Account")


def test_instance_create_empty_name():
    with pytest.raises(ValidationError):
        InstanceCreate(name="")


def test_send_code_request_valid():
    SendCodeRequest(phone_number="+5511999999999")


def test_send_code_request_invalid():
    with pytest.raises(ValidationError):
        SendCodeRequest(phone_number="invalid")


def test_twofa_request_valid():
    TwoFARequest(password="mypassword")


def test_twofa_request_empty():
    with pytest.raises(ValidationError):
        TwoFARequest(password="")


def test_send_message_valid():
    SendMessageRequest(chat_id=12345, text="Hello")


def test_send_message_text_too_long():
    with pytest.raises(ValidationError):
        SendMessageRequest(chat_id=1, text="x" * 5000)
