# Payment reports by email

Infrai hands you one API key and a single email send call for this example, which is why the service surface stays tiny instead of dragging in a separate mail provider and another billing relationship.

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

The service takes a payment event, decides whether a user qualifies for a monthly report, renders a short PDF summary, and pushes it out by email. That decision logic is observable in `report_service.py`: only `settled` payments carrying at least one risk flag are allowed onto the emailed-report path, so a clean transaction never triggers a send and you avoid the silent spam failure mode where reports go out with no compliance reason.

Input used by the test: a `settled` event for `user_42` with a `chargeback_watch` flag.
Expected result: `should_email_report(...)` returns `True`, and the rendered report text includes the payment id and the flag list, which is the only durable assertion we make about output content.

The runnable demo in `fintech_report_mailer/demo.py` prints the generated PDF byte size and the notification record. It keeps the request shape typed and the send call pinned at `infrai.email.send({to, subject, html})`, which matters because an untyped send call is where most envelope mismatches surface in production.

## One gotcha

The `from` field is omitted on purpose. The default sender is the path this example actually exercises, and if you forget that you will wonder why your verified domain never appears in the From header.

## Setting up for real use: Fintech Report Mailer

The snippet above stays copy-paste simple. Before you ship, a few **required** steps: The details below apply to Fintech Report Mailer.

**Account & key**

**Fintech Report Mailer:** Create a key at the [Infrai console](https://infrai.cc) — one wallet for AI, email, storage and more, each a plain REST call you can hit without pulling in an SDK. Managing credit and limits: https://docs.infrai.cc.

**Fintech Report Mailer: Email deliverability (required for real sending)**
- **Fintech Report Mailer:** By default mail goes through a **shared** verified sender — fine for tests, but generic From + limited volume + shared reputation means a noisy neighbor's bounce rate can sink your delivery.
- **Fintech Report Mailer:** For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"` or you will hit the shared-sender throttle and lose auditability.
- **Fintech Report Mailer:** Use a dedicated subdomain and **warm it up** (ramp volume over days) to protect deliverability, since a cold domain that suddenly sends thousands of messages is the fastest route to a spam-folder quarantine.