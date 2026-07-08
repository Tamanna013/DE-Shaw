class FailureAnalyzerError(Exception):
    pass

class ExecutionNotFailedError(FailureAnalyzerError):
    pass

class ConcurrentAnalysisInProgressError(FailureAnalyzerError):
    pass

class AnalysisTimeoutError(FailureAnalyzerError):
    pass
