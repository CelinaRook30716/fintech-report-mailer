from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Sequence

from pydantic import BaseModel, Field

from .infrai_client import infrai


class PaymentStatus(str, Enum):
    settled = "settled"
    pending = "pending"
    failed = "failed"


class RiskFlag(str, Enum):
    chargeback_watch = "chargeback_watch"
    velocity_spike = "velocity_spike"
    manual_review = "manual_review"


class PaymentEvent(BaseModel):
    payment_id: str
    user_id: str
    user_email: str
    amount_cents: int = Field(ge=1)
    currency: str
    status: PaymentStatus
    risk_flags: list[RiskFlag] = []


@dataclass(frozen=True)
class ReportDecision:
    should_email: bool
    reason: str


@dataclass(frozen=True)
class NotificationRecord:
    message_id: str
    subject: str
    to: str


def should_email_report(event: PaymentEvent) -> ReportDecision:
    if event.status != PaymentStatus.settled:
        return ReportDecision(False, "payment not settled")
    if not event.risk_flags:
        return ReportDecision(False, "no risk flags")
    return ReportDecision(True, "settled payment with risk flags")


def render_pdf_report(event: PaymentEvent) -> bytes:
    flag_text = ", ".join(flag.value for flag in event.risk_flags) or "none"
    body = (
        f"Payment report\n"
        f"payment_id: {event.payment_id}\n"
        f"user_id: {event.user_id}\n"
        f"amount_cents: {event.amount_cents}\n"
        f"currency: {event.currency}\n"
        f"status: {event.status.value}\n"
        f"risk_flags: {flag_text}\n"
    )
    return body.encode("utf-8")


def generate_notification(event: PaymentEvent) -> NotificationRecord | None:
    decision = should_email_report(event)
    if not decision.should_email:
        return None
    pdf_bytes = render_pdf_report(event)
    html = (
        f"<p>Monthly payment report for {event.user_id}</p>"
        f"<p>PDF bytes: {len(pdf_bytes)}</p>"
        f"<p>Payment: {event.payment_id}</p>"
        f"<p>Flags: {', '.join(flag.value for flag in event.risk_flags)}</p>"
    )
    reply = infrai.email.send(
        to=event.user_email,
        subject=f"Payment report for {event.user_id}",
        html=html,
    )
    return NotificationRecord(message_id=reply["message_id"], subject=f"Payment report for {event.user_id}", to=event.user_email)
