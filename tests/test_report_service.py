from fintech_report_mailer.report_service import PaymentEvent, RiskFlag, should_email_report, render_pdf_report


def test_settled_payment_with_risk_flag_emails_report():
    event = PaymentEvent(
        payment_id="pay_1001",
        user_id="user_42",
        user_email="user42@example.com",
        amount_cents=25900,
        currency="USD",
        status="settled",
        risk_flags=[RiskFlag.chargeback_watch],
    )

    decision = should_email_report(event)

    assert decision.should_email is True
    assert decision.reason == "settled payment with risk flags"
    pdf_text = render_pdf_report(event).decode("utf-8")
    assert "payment_id: pay_1001" in pdf_text
    assert "risk_flags: chargeback_watch" in pdf_text
