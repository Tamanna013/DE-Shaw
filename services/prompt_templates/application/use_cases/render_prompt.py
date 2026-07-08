from pydantic import ValidationError
from jinja2 import Template
from services.prompt_templates.application.ports import PromptTemplateRepositoryPort
from services.prompt_templates.domain.exceptions import MissingContextFieldError
from shared.logging_engine import get_logger

logger = get_logger(__name__)

class RenderPromptUseCase:
    def __init__(self, repo: PromptTemplateRepositoryPort):
        self.repo = repo

    def execute(self, template_name: str, version: str, context: dict) -> str:
        # 1. Fetch template
        template = self.repo.get_template(template_name, version)
        
        # 2. Validate Context using the template's Pydantic schema
        try:
            validated_context = template.input_schema(**context)
        except ValidationError as e:
            # Pydantic validation errors can be complex, extract exactly which fields failed
            missing_fields = []
            for err in e.errors():
                loc = ".".join([str(l) for l in err["loc"]])
                msg = err["msg"]
                missing_fields.append(f"{loc}: {msg}")
                
            error_msg = f"Failed to validate context for {template_name} v{version}.\nValidation Errors:\n" + "\n".join(missing_fields)
            logger.error(error_msg)
            raise MissingContextFieldError(error_msg)
            
        # 3. Render Jinja2 template
        jinja_template = Template(template.template_content)
        rendered = jinja_template.render(**validated_context.model_dump())
        
        return rendered
