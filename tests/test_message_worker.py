from unittest.mock import AsyncMock, patch

import pytest


@pytest.mark.asyncio
async def test_worker_processes_job():
    job = {
        "job_id": "job-1", "type": "send_text",
        "payload": '{"chat_id": 1, "text": "hello"}',
        "attempt_count": "0", "max_retries": "3",
    }

    mock_dequeue = AsyncMock()
    mock_dequeue.side_effect = [job, None]

    with patch("app.workers.message_worker.dequeue", mock_dequeue), \
         patch("app.workers.message_worker.is_paused", AsyncMock(return_value=False)), \
         patch("app.workers.message_worker.check_ratelimit", AsyncMock(return_value=(True, 0))), \
         patch("app.workers.message_worker.svc_send_message", AsyncMock(return_value={"message_id": 42})), \
         patch("app.workers.message_worker.update_job", AsyncMock()), \
         patch("app.workers.message_worker.set_flood_wait", AsyncMock()), \
         patch("app.workers.message_worker.dead_letter", AsyncMock()), \
         patch("app.workers.message_worker._requeue", AsyncMock()):

        from app.workers.message_worker import process_instance
        await process_instance("00000000-0000-0000-0000-000000000001")


@pytest.mark.asyncio
async def test_worker_skips_paused_instance():
    with patch("app.workers.message_worker.is_paused", AsyncMock(return_value=True)), \
         patch("app.workers.message_worker.dequeue") as mock_dequeue:

        from app.workers.message_worker import process_instance
        await process_instance("inst-1")
        mock_dequeue.assert_not_called()
