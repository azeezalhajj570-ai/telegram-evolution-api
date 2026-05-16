# Quickstart: Rich Messaging

## New Dependencies

```bash
pip install python-multipart aiofiles
```

## Testing Media Sends

```bash
# Create a small test image
python3 -c "
from PIL import Image
img = Image.new('RGB', (100, 100), color='red')
img.save('/tmp/test_photo.jpg')
"

# Send photo
curl -X POST http://localhost:8100/instances/$ID/messages/send-photo \
  -H "Authorization: Bearer dev-key-1" \
  -F "chat_id=8078506561" \
  -F "file=@/tmp/test_photo.jpg" \
  -F "caption=Hello from the gateway!"

# Reply to a message
curl -X POST http://localhost:8100/instances/$ID/messages/reply \
  -H "Authorization: Bearer dev-key-1" \
  -H "Content-Type: application/json" \
  -d '{"chat_id": 8078506561, "text": "This is a reply", "reply_to": 37893}'

# Forward a message
curl -X POST http://localhost:8100/instances/$ID/messages/forward \
  -H "Authorization: Bearer dev-key-1" \
  -H "Content-Type: application/json" \
  -d '{"from_chat_id": 8078506561, "message_id": 37893, "to_chat_id": 8078506561}'

# Edit a message
curl -X PATCH http://localhost:8100/instances/$ID/messages/37893 \
  -H "Authorization: Bearer dev-key-1" \
  -H "Content-Type: application/json" \
  -d '{"text": "Updated text!"}'

# Delete a message
curl -X DELETE "http://localhost:8100/instances/$ID/messages/37893?chat_id=8078506561" \
  -H "Authorization: Bearer dev-key-1"

# Add a reaction
curl -X POST http://localhost:8100/instances/$ID/messages/37893/reaction \
  -H "Authorization: Bearer dev-key-1" \
  -H "Content-Type: application/json" \
  -d '{"emoji": "👍"}'

# Download media from a message
curl http://localhost:8100/instances/$ID/messages/42/media?chat_id=8078506561 \
  -H "Authorization: Bearer dev-key-1" \
  -o /tmp/downloaded.jpg
```

## Run Tests

```bash
pytest tests/test_media.py tests/test_message_actions.py tests/test_reactions.py -v
```
