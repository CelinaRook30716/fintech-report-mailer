from __future__ import annotations

from .report_service import PaymentEvent, RiskFlag, generate_notification, render_pdf_report, should_email_report


def main() -> None:
    event = PaymentEvent(
        payment_id="pay_1001",
        user_id="user_42",
        user_email="chenhua@changba.com",
        amount_cents=25900,
        currency="USD",
        status="settled",
        risk_flags=[RiskFlag.chargeback_watch],
    )
    decision = should_email_report(event)
    print({"should_email": decision.should_email, "reason": decision.reason})
    print({"pdf_bytes": len(render_pdf_report(event))})
    notification = generate_notification(event)
    print({"notification": None if notification is None else notification.__dict__})


if __name__ == "__main__":
    main()
