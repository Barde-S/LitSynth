"""
Progress Manager for Document Upload Processing

Manages upload progress state and provides pub/sub mechanism for SSE streaming.
"""

import asyncio
from typing import Dict, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class FileProgress:
    """Progress state for a single file"""
    filename: str
    stage: str = "pending"  # pending, uploading, ocr, chunking, embedding, indexing, complete, error
    progress: int = 0  # 0-100
    error: Optional[str] = None
    pages: Optional[int] = None
    chunks: Optional[int] = None


@dataclass
class UploadProgress:
    """Progress state for an entire upload batch"""
    upload_id: str
    workspace_id: str
    files: Dict[str, FileProgress] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed: bool = False


class ProgressManager:
    """
    Singleton manager for tracking upload progress across multiple concurrent uploads.
    Provides pub/sub mechanism for SSE streaming to clients.
    """

    def __init__(self):
        self._progress: Dict[str, UploadProgress] = {}
        self._subscribers: Dict[str, List[asyncio.Queue]] = {}
        self._lock = asyncio.Lock()

    def create_upload(
        self,
        upload_id: str,
        workspace_id: str,
        filenames: List[str]
    ) -> UploadProgress:
        """Create a new upload progress tracker"""
        progress = UploadProgress(
            upload_id=upload_id,
            workspace_id=workspace_id,
            files={f: FileProgress(filename=f) for f in filenames}
        )
        self._progress[upload_id] = progress
        self._subscribers[upload_id] = []
        logger.info(f"Created progress tracker for upload {upload_id} with {len(filenames)} files")
        return progress

    async def update_file_progress(
        self,
        upload_id: str,
        filename: str,
        stage: str,
        progress: int = 0,
        error: Optional[str] = None,
        pages: Optional[int] = None,
        chunks: Optional[int] = None
    ):
        """Update progress for a specific file and notify subscribers"""
        if upload_id not in self._progress:
            logger.warning(f"Upload {upload_id} not found for progress update")
            return

        file_progress = self._progress[upload_id].files.get(filename)
        if file_progress:
            file_progress.stage = stage
            file_progress.progress = progress
            if error is not None:
                file_progress.error = error
            if pages is not None:
                file_progress.pages = pages
            if chunks is not None:
                file_progress.chunks = chunks

            logger.debug(f"Updated {filename}: stage={stage}, progress={progress}%")

        # Notify all subscribers
        await self._notify(upload_id)

    def subscribe(self, upload_id: str) -> asyncio.Queue:
        """Subscribe to progress updates for an upload"""
        queue: asyncio.Queue = asyncio.Queue()
        if upload_id in self._subscribers:
            self._subscribers[upload_id].append(queue)
            logger.info(f"New subscriber for upload {upload_id}, total: {len(self._subscribers[upload_id])}")
        return queue

    def unsubscribe(self, upload_id: str, queue: asyncio.Queue):
        """Unsubscribe from progress updates"""
        if upload_id in self._subscribers:
            try:
                self._subscribers[upload_id].remove(queue)
                logger.debug(f"Subscriber removed for upload {upload_id}")
            except ValueError:
                pass

    async def _notify(self, upload_id: str):
        """Send progress update to all subscribers"""
        if upload_id not in self._subscribers:
            return

        progress = self._progress[upload_id]
        data = {
            "upload_id": upload_id,
            "files": {
                f: {
                    "stage": fp.stage,
                    "progress": fp.progress,
                    "error": fp.error,
                    "pages": fp.pages,
                    "chunks": fp.chunks
                }
                for f, fp in progress.files.items()
            },
            "completed": progress.completed
        }

        for queue in self._subscribers[upload_id]:
            try:
                await queue.put(data)
            except Exception as e:
                logger.error(f"Failed to notify subscriber: {e}")

    async def mark_complete(self, upload_id: str):
        """Mark an upload as complete and notify subscribers"""
        if upload_id in self._progress:
            self._progress[upload_id].completed = True
            await self._notify(upload_id)
            logger.info(f"Upload {upload_id} marked as complete")

    def get_progress(self, upload_id: str) -> Optional[UploadProgress]:
        """Get current progress state for an upload"""
        return self._progress.get(upload_id)

    def cleanup(self, upload_id: str):
        """Clean up progress data for completed upload"""
        self._progress.pop(upload_id, None)
        self._subscribers.pop(upload_id, None)
        logger.debug(f"Cleaned up progress data for upload {upload_id}")

    def cleanup_stale(self, max_age_seconds: int = 3600):
        """Clean up stale uploads older than max_age_seconds"""
        now = datetime.utcnow()
        stale_ids = [
            uid for uid, up in self._progress.items()
            if (now - up.created_at).total_seconds() > max_age_seconds
        ]
        for uid in stale_ids:
            self.cleanup(uid)
        if stale_ids:
            logger.info(f"Cleaned up {len(stale_ids)} stale uploads")


# Global singleton instance
progress_manager = ProgressManager()
