import importlib.util
import json
from io import BytesIO
from pathlib import Path
from urllib.error import URLError


SCRIPT = Path(__file__).parents[1] / "scripts" / "wait_for_video.py"
SPEC = importlib.util.spec_from_file_location("wait_for_video", SCRIPT)
waiter = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(waiter)


class Clock:
    def __init__(self):
        self.now = 0.0

    def monotonic(self):
        return self.now

    def sleep(self, seconds):
        self.now += seconds


def read_status(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_waiter_downloads_completed_video_atomically(tmp_path):
    clock = Clock()
    responses = iter([
        {"status": "pending", "queue_position": 2},
        {"status": "processing"},
        {"status": "completed", "video_url": "https://signed.example/video"},
    ])
    output = tmp_path / "result.mp4"
    status = tmp_path / "result.status.json"

    def download(_url, destination):
        destination.write_bytes(b"video")

    result = waiter.wait_for_video(
        task_id="internal-task",
        api_key="secret-key",
        output_file=output,
        status_file=status,
        poll_interval=20,
        timeout=100,
        task_requester=lambda *_args: next(responses),
        video_downloader=download,
        monotonic=clock.monotonic,
        sleeper=clock.sleep,
    )

    assert result == 0
    assert output.read_bytes() == b"video"
    assert read_status(status)["status"] == "completed"
    assert "secret-key" not in status.read_text(encoding="utf-8")


def test_waiter_records_failed_task(tmp_path):
    output = tmp_path / "result.mp4"
    status = tmp_path / "result.status.json"
    result = waiter.wait_for_video(
        task_id="internal-task",
        api_key="secret-key",
        output_file=output,
        status_file=status,
        task_requester=lambda *_args: {
            "status": "failed",
            "error_code": "DIGITAL_HUMAN_GENERATION_FAILED",
        },
    )

    payload = read_status(status)
    assert result == 1
    assert payload["status"] == "failed"
    assert not output.exists()


def test_waiter_records_cancelled_task(tmp_path):
    status = tmp_path / "result.status.json"
    result = waiter.wait_for_video(
        task_id="internal-task",
        api_key="secret-key",
        output_file=tmp_path / "result.mp4",
        status_file=status,
        task_requester=lambda *_args: {"status": "cancelled"},
    )

    assert result == 1
    assert read_status(status)["status"] == "cancelled"


def test_waiter_retries_temporary_network_error(tmp_path):
    clock = Clock()
    calls = iter([URLError("temporary"), {"status": "completed", "video_url": "https://signed"}])

    def request(*_args):
        value = next(calls)
        if isinstance(value, Exception):
            raise value
        return value

    result = waiter.wait_for_video(
        task_id="internal-task",
        api_key="secret-key",
        output_file=tmp_path / "result.mp4",
        status_file=tmp_path / "result.status.json",
        poll_interval=20,
        timeout=60,
        task_requester=request,
        video_downloader=lambda _url, path: path.write_bytes(b"video"),
        monotonic=clock.monotonic,
        sleeper=clock.sleep,
    )

    assert result == 0


def test_download_video_uses_partial_then_atomic_rename(tmp_path, monkeypatch):
    destination = tmp_path / "result.mp4"
    monkeypatch.setattr(waiter, "urlopen", lambda *_args, **_kwargs: BytesIO(b"video"))

    waiter.download_video("https://signed", destination)

    assert destination.read_bytes() == b"video"
    assert not destination.with_suffix(".mp4.part").exists()


def test_waiter_timeout_keeps_task_resumable(tmp_path):
    clock = Clock()
    output = tmp_path / "result.mp4"
    status = tmp_path / "result.status.json"
    result = waiter.wait_for_video(
        task_id="internal-task",
        api_key="secret-key",
        output_file=output,
        status_file=status,
        poll_interval=20,
        timeout=40,
        task_requester=lambda *_args: {"status": "processing"},
        monotonic=clock.monotonic,
        sleeper=clock.sleep,
    )

    payload = read_status(status)
    assert result == 2
    assert payload["status"] == "timeout"
    assert payload["task_status"] == "still_processing"
    assert "Run the waiter again" in payload["message"]

    resumed = waiter.wait_for_video(
        task_id="internal-task",
        api_key="secret-key",
        output_file=output,
        status_file=status,
        task_requester=lambda *_args: {
            "status": "completed",
            "video_url": "https://signed",
        },
        video_downloader=lambda _url, path: path.write_bytes(b"video"),
    )

    assert resumed == 0
    assert read_status(status)["status"] == "completed"
    assert output.read_bytes() == b"video"
