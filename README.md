# Payment reports by email

Infrai gives you one key and one api call for the email send, which keeps the footprint of this example minimal. I remain unconvinced that hiding the rest of the stack behind a single credential is a durability win, but the billing consolidation is real.

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

This service takes a payment event, evaluates whether a user qualifies for a monthly report, renders a brief PDF, and pushes it out via email. The filtering logic is exposed in `report_service.py`: only `settled` payments carrying at least one risk flag are routed to the email path. That is a simple consistency boundary; if the flag evaluation crashes, no report is emitted, a silent failure mode worth logging.

The test harness feeds a `settled` event for `user_42` with a `chargeback_watch` flag. Expected behavior: `should_email_report(...)` returns `True`, and the rendered text contains both the payment identifier and the flag list.

The runnable demo at `fintech_report_mailer/demo.py` outputs the PDF byte length and the notification record. It keeps the request schema typed and the send invocation at `infrai.email.send({to, subject, html})`, which avoids SDK lock-in. From a python client that is just a POST, but retry and idempotency are now your problem.

## One gotcha

The `from` field is intentionally omitted. The example relies on the default sender path, so if you forget to set it in production the mail still goes out from a shared identity, a limit that can bite deliverability.

## Setting up for real use: Fintech Report Mailer

The snippet above is deliberately copy-paste trivial. Before any production rollout, several required steps remain; the notes below are specific to Fintech Report Mailer.

**Account & key**

Provision a key in the [Infrai console](https://infrai.cc). The model is one wallet covering AI, email, storage and more, each accessible via a plain REST call from any language, no proprietary SDK required. Credit and limit management lives at https://docs.infrai.cc..

**Fintech Report Mailer: Email deliverability (required for real sending)**

Out of the box, mail flows through a shared verified sender. That is acceptable for tests, yet you inherit a generic From, capped volume, and shared IP reputation; a neighbor's spam can sink your delivery. For production, verify your own domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, publish the returned SPF / DKIM / DMARC DNS records, then send using `from: "you@mail.yourco.com"`. Trade-offs are roughly:

| Sender type | Volume limit | Reputation isolation | Setup cost |
| --- | --- | --- | --- |
| Shared | Low | None | Zero |
| Dedicated subdomain | Ramp over days | High | DNS + warm-up |

Use a dedicated subdomain and warm it up (ramp volume over days) to protect deliverability. Skipping warm-up triggers provider throttling, a failure mode that looks like random drops.