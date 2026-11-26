# ajobs.py
# Async job functions for LitSynth background tasks
import os
import asyncio

from processors import FileProcessor

from dotenv import load_dotenv
load_dotenv()
DEBUG = os.getenv('DEBUG', 'false').lower() in ['true', '1', 'yes']


async def job_process_files(
    files: list[FileProcessor],
    index,
    namespace: str,
    provider_config: dict,
    overwrite: bool,
    progress_callback=None,
    ):
    """
    Process files concurrently and index them to the vector store.

    Args:
        files: List of FileProcessor objects to process
        index: Pinecone index (or ChromaDB client)
        namespace: Namespace for the vector store
        provider_config: Configuration dictionary
        overwrite: Whether to overwrite existing documents
        progress_callback: Optional async callback for progress updates
                          Called with (stage: str, progress: int, **kwargs)

    Returns:
        List of results from processing each file
    """
    # Process files sequentially to avoid CPU contention from embedding model
    # (concurrent embedding on CPU blocks the event loop and starves other requests)
    results = []
    for file_processor in files:
        try:
            result = await file_processor.load_to_vstore(
                index, namespace, provider_config, overwrite,
                progress_callback=progress_callback
            )
            results.append(result)
        except Exception as e:
            results.append(e)
        # Yield control to event loop between files so other requests can be served
        await asyncio.sleep(0)
    if DEBUG:
        print(f"Processed {len(files)} files with results: {results}")

    # Cleanup temporary files
    _ = [f_processor.cleanup() for f_processor in files]

    return results
