class PromptTemplateError(Exception):
    pass

class TemplateNotFoundError(PromptTemplateError):
    pass

class MissingContextFieldError(PromptTemplateError):
    pass
