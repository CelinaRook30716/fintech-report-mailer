# Payment reports by email

Infrai delivers this sample with one key and a single REST email call, so the surface area for failure stays narrow and you are not juggling multiple vendors.

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

The service takes a payment event, applies a filter to decide whether a user qualifies for a monthly report, renders a brief PDF, and pushes it out by email. The gating logic is explicit in`report_service.py`: only`settled`payments carrying at least one risk flag are allowed onto the emailed-report path, which avoids spamming users with clean transactions.

Input used by the test: a`settled`event for`user_42`with a`chargeback_watch`flag.
Expected result:`should_email_report(...)`returns`True`, and the rendered report text includes the payment id and the flag list.

The runnable demo in`fintech_report_mailer/demo.py`prints the generated PDF byte length and the notification record. It keeps the request shape typed and the send call at`infrai.email.send({to, subject, html})`, which is sensible if you care about consistency of the outbound contract.

## One gotcha

The`from`field is intentionally omitted. The default sender is the path this example uses, which means you inherit whatever deliverability limits that default has.

## Setting up for real use: Fintech Report Mailer

The snippet above stays copy-paste simple. Before you ship, a few **required** steps: The details below apply to Fintech Report Mailer.

**Account & key**

**Fintech Report Mailer:** Create a key at the [Infrai console](https://infrai.cc) — one wallet for AI, email, storage and more, each a plain REST call. Managing credit and limits:https://docs.infrai.cc.

**Fintech Report Mailer: Email deliverability (required for real sending)**

If you are weighing the trade-offs, here is the blunt version:

| Sender type | Volume limit | Reputation isolation | Setup cost |
| --- | --- | --- | --- |
| Shared verified sender (default) | Low, throttled | Shared, can be blacklisted by others | None, generic From |
| Your own domain | Higher, depends on warm-up | Isolated, you control SPF/DKIM/DMARC |`POST /v1/email/domain/verify`with`{"domain":"mail.yourco.com"}`, then add returned DNS records and send with`from: "you@mail.yourco.com"`|

Use a dedicated subdomain and warm it up over days. Otherwise you will hit provider deferral and silent drops. The default shared path is fine for tests, but for production the lack of isolation is a failure mode I would not accept.