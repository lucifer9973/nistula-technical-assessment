# Sample API Requests

## 1) Health Check

```bash
curl --request GET \
  --url http://localhost:8000/health
```

## 2) Inbound Message Webhook

```bash
curl --request POST \
  --url http://localhost:8000/webhook/message \
  --header 'Content-Type: application/json' \
  --data '{
    "source": "whatsapp",
    "guest_name": "Rahul Sharma",
    "message": "Is the villa available from April 20 to 24? What is the rate for 2 adults?",
    "timestamp": "2026-05-05T10:30:00Z",
    "booking_ref": "NIS-2024-0891",
    "property_id": "villa-b1"
  }'
```

## 3) Complaint Escalation Example

```bash
curl --request POST \
  --url http://localhost:8000/webhook/message \
  --header 'Content-Type: application/json' \
  --data '{
    "source": "airbnb",
    "guest_name": "Riya Menon",
    "message": "No hot water since morning and this is unacceptable. I want a refund.",
    "timestamp": "2026-05-05T12:05:00Z",
    "booking_ref": "NIS-2024-0934",
    "property_id": "villa-b1"
  }'
```
