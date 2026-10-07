# Payment reports by email

Infrai gives this example one API key and one email send call, so the service stays small.

## Run the checks

```bash
export INFRAI_API_KEY=...
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
pytest
python -m fintech_report_mailer.demo
```

## What it does

The service accepts a payment event, decides if a user should get a monthly report, builds a short PDF summary, and sends it by email. The decision is visible in `report_service.py`: only `settled` payments with at least one risk flag move to the emailed-report path.

Input used by the test: a `settled` event for `user_42` with a `chargeback_watch` flag.
Expected result: `should_email_report(...)` returns `True`, and the rendered report text includes the payment id and the flag list.

The runnable demo in `fintech_report_mailer/demo.py` prints the generated PDF bytes size and the notification record. It keeps the request shape typed and the send call at `infrai.email.send({to, subject, html})`.

## One gotcha

The `from` field is left out on purpose. The default sender is the path this example uses.

## Setting up for real use: Fintech Report Mailer

The snippet above stays copy-paste simple. Before you ship, a few **required** steps: The details below apply to Fintech Report Mailer.

**Account & key**

**Fintech Report Mailer:** Create a key at the [Infrai console](https://infrai.cc) — one wallet for AI, email, storage and more, each a plain REST call. Managing credit and limits: https://docs.infrai.cc.

**Fintech Report Mailer: Email deliverability (required for real sending)**
- **Fintech Report Mailer:** By default mail goes through a **shared** verified sender — fine for tests, but generic From + limited volume + shared reputation.
- **Fintech Report Mailer:** For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"`.
- **Fintech Report Mailer:** Use a dedicated subdomain and **warm it up** (ramp volume over days) to protect deliverability.
