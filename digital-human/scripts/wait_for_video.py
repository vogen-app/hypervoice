#!/usr/bin/env python3
"""Wait for a VoGen digital-human task and download its completed video."""

from __future__ import annotations

import argparse
import json
import logging
import os
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


DEFAULT_BASE_URL = "https://api.vogen.app/v1/digital-human"
DEFAULT_OUTPUT_DIR = "./vogen-output"
DEFAULT_POLL_INTERVAL_SECONDS = 20.0
DEFAULT_TIMEOUT_SECONDS = 90 * 60.0
TRANSIENT_HTTP_STATUSES = {408, 425, 429, 500, 502, 503, 504}
ACTIVE_STATUSES = {"pending", "started", "processing"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_status(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def request_task(base_url: str, task_id: str, api_key: str) -> dict[str, Any]:
    request = Request(
        f"{base_url.rstrip('/')}/tasks/{task_id}",
        headers={"Authorization": f"Bearer {api_key}", "Accept": "application/json"},
    )
    with urlopen(request, timeout=30) as response:
        return json.load(response)


def download_video(url: str, destination: Path) -> None:
    partial = destination.with_suffix(destination.suffix + ".part")
    try:
        request = Request(url, headers={"Accept": "video/*"})
        with urlopen(request, timeout=120) as response, partial.open("wb") as output:
            shutil.copyfileobj(response, output, length=1024 * 1024)
        if partial.stat().st_size < 1:
            raise ValueError("The downloaded video is empty")
        os.replace(partial, destination)
    except Exception:
        partial.unlink(missing_ok=True)
        raise


def error_detail(exc: HTTPError) -> tuple[str, str]:
    try:
        body = json.loads(exc.read().decode("utf-8"))
        detail = body.get("detail") if isinstance(body, dict) else None
        if isinstance(detail, dict):
            return str(detail.get("code") or f"HTTP_{exc.code}"), str(
                detail.get("message") or "Request failed"
            )
    except Exception:
        pass
    return f"HTTP_{exc.code}", "Request failed"


def wait_for_video(
    *,
    task_id: str,
    api_key: str,
    output_file: Path,
    status_file: Path,
    base_url: str = DEFAULT_BASE_URL,
    poll_interval: float = DEFAULT_POLL_INTERVAL_SECONDS,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
    task_requester: Callable[[str, str, str], dict[str, Any]] = request_task,
    video_downloader: Callable[[str, Path], None] = download_video,
    monotonic: Callable[[], float] = time.monotonic,
    sleeper: Callable[[float], None] = time.sleep,
) -> int:
    started = monotonic()
    base_state = {
        "task_id": task_id,
        "output_file": str(output_file.resolve()),
        "started_at": utc_now(),
    }
    write_status(status_file, {**base_state, "status": "waiting", "updated_at": utc_now()})

    while monotonic() - started < timeout:
        try:
            task = task_requester(base_url, task_id, api_key)
        except HTTPError as exc:
            code, message = error_detail(exc)
            if exc.code not in TRANSIENT_HTTP_STATUSES:
                write_status(status_file, {
                    **base_state,
                    "status": "error",
                    "error_code": code,
                    "message": message,
                    "updated_at": utc_now(),
                })
                logging.error("Task status request stopped: %s", code)
                return 1
            logging.warning("Temporary HTTP %s while checking task; retrying", exc.code)
        except (URLError, TimeoutError, OSError) as exc:
            logging.warning("Temporary network error while checking task; retrying: %s", type(exc).__name__)
        else:
            task_status = str(task.get("status") or "unknown")
            if task_status == "completed":
                video_url = task.get("video_url")
                if not video_url:
                    logging.warning("Completed task has no video URL yet; retrying")
                else:
                    try:
                        output_file.parent.mkdir(parents=True, exist_ok=True)
                        video_downloader(str(video_url), output_file)
                    except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
                        logging.warning("Temporary video download error; retrying: %s", type(exc).__name__)
                    else:
                        write_status(status_file, {
                            **base_state,
                            "status": "completed",
                            "task_status": "completed",
                            "completed_at": utc_now(),
                            "updated_at": utc_now(),
                        })
                        logging.info("Video saved to %s", output_file.resolve())
                        return 0
            elif task_status in {"failed", "cancelled"}:
                write_status(status_file, {
                    **base_state,
                    "status": task_status,
                    "task_status": task_status,
                    "error_code": task.get("error_code"),
                    "updated_at": utc_now(),
                })
                logging.error("Digital-human task ended with status %s", task_status)
                return 1
            elif task_status in ACTIVE_STATUSES:
                write_status(status_file, {
                    **base_state,
                    "status": "waiting",
                    "task_status": task_status,
                    "queue_position": task.get("queue_position"),
                    "updated_at": utc_now(),
                })
                logging.info("Task status: %s", task_status)
            else:
                logging.warning("Unknown task status %s; retrying", task_status)

        sleeper(poll_interval)

    write_status(status_file, {
        **base_state,
        "status": "timeout",
        "task_status": "still_processing",
        "message": "The task was not cancelled. Run the waiter again to continue checking it.",
        "updated_at": utc_now(),
    })
    logging.warning("Wait timeout reached; the server-side task is still active")
    return 2


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task-id", required=True, help="Internal task ID returned by VoGen")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--filename", help="Output MP4 basename")
    parser.add_argument("--poll-interval", type=float, default=DEFAULT_POLL_INTERVAL_SECONDS)
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.poll_interval <= 0 or args.timeout <= 0:
        raise SystemExit("--poll-interval and --timeout must be positive")

    output_dir = Path(args.output_dir).expanduser().resolve()
    filename = args.filename or f"digital-human-{datetime.now():%Y%m%d-%H%M%S}.mp4"
    if Path(filename).name != filename or not filename.lower().endswith(".mp4"):
        raise SystemExit("--filename must be an MP4 basename without directories")

    api_key = os.environ.get("VOGEN_API_KEY")
    if not api_key:
        raise SystemExit("VOGEN_API_KEY is required")

    output_dir.mkdir(parents=True, exist_ok=True)
    stem = Path(filename).stem
    output_file = output_dir / filename
    status_file = output_dir / f"{stem}.status.json"
    log_file = output_dir / f"{stem}.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[logging.FileHandler(log_file, encoding="utf-8"), logging.StreamHandler(sys.stdout)],
    )
    logging.info("Waiting for digital-human generation; output=%s", output_file)
    return wait_for_video(
        task_id=args.task_id,
        api_key=api_key,
        output_file=output_file,
        status_file=status_file,
        base_url=args.base_url,
        poll_interval=args.poll_interval,
        timeout=args.timeout,
    )


if __name__ == "__main__":
    raise SystemExit(main())
