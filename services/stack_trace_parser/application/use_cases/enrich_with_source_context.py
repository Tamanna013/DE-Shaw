from services.stack_trace_parser.domain.entities import StackTrace
from services.stack_trace_parser.application.ports import SourceCodeFetcherPort
from shared.logging_engine import get_logger

logger = get_logger(__name__)

class EnrichWithSourceContextUseCase:
    def __init__(self, source_fetcher: SourceCodeFetcherPort):
        self.source_fetcher = source_fetcher

    async def execute(self, trace: StackTrace, commit_sha: str) -> StackTrace:
        if trace.root_exception.language == "unknown" or trace.root_exception.needs_sourcemap:
            return trace
            
        enriched_count = 0
        for frame in trace.root_exception.frames:
            if frame.is_external or not frame.line_number:
                continue
                
            try:
                context = await self.source_fetcher.fetch_context(commit_sha, frame.file_path, frame.line_number)
                if context:
                    frame.code_context = context
                    enriched_count += 1
            except Exception as e:
                logger.warning("Failed to fetch source context", file=frame.file_path, exc_info=e)
                
        if enriched_count > 0:
            logger.info("Enriched frames with source context", count=enriched_count)
            
        return trace
