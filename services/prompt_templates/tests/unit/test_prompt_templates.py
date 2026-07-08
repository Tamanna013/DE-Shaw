import pytest
import os
from services.prompt_templates.infrastructure.file_repository import FileBasedPromptTemplateRepository
from services.prompt_templates.application.use_cases.render_prompt import RenderPromptUseCase
from services.prompt_templates.domain.exceptions import MissingContextFieldError

@pytest.fixture
def repo():
    # Uses the real templates directory for integration-style unit testing
    return FileBasedPromptTemplateRepository()
    
@pytest.fixture
def render_uc(repo):
    return RenderPromptUseCase(repo)

@pytest.mark.parametrize("template_name, version", [
    ("failure_root_cause", "v1"),
    ("failure_root_cause", "v2"),
    ("test_case_suggestion", "v1"),
    ("flaky_explanation", "v1")
])
def test_all_templates_render_without_error_given_valid_schema_instance(render_uc, repo, template_name, version):
    template = repo.get_template(template_name, version)
    
    # Generate valid example context directly from the co-located Pydantic schema
    valid_context = template.input_schema.generate_example()
    
    # Render it
    rendered = render_uc.execute(template_name, version, valid_context)
    
    assert rendered
    assert isinstance(rendered, str)
    assert len(rendered) > 50

def test_missing_required_field_raises_clear_error(render_uc):
    # flaky_explanation requires test_case_name, passes, fails
    invalid_context = {"test_case_name": "test_foo"} # Missing passes and fails
    
    with pytest.raises(MissingContextFieldError) as exc_info:
        render_uc.execute("flaky_explanation", "v1", invalid_context)
        
    error_msg = str(exc_info.value)
    assert "passes: Field required" in error_msg
    assert "fails: Field required" in error_msg

def test_rendered_prompt_contains_json_schema_instructions(render_uc, repo):
    template = repo.get_template("failure_root_cause", "v1")
    valid_context = template.input_schema.generate_example()
    
    rendered = render_uc.execute("failure_root_cause", "v1", valid_context)
    
    # Assert critical anti-hallucination instruction is present
    assert "CRITICAL INSTRUCTION" in rendered
    assert "ONLY cite evidence actually present" in rendered
    
    # Assert JSON schema instruction is present
    assert "JSON" in rendered
    assert "hypotheses" in rendered

def test_template_versioning_v1_and_v2_both_loadable_independently(render_uc, repo):
    # Ensure they both load and have different structural properties if needed
    t1 = repo.get_template("failure_root_cause", "v1")
    t2 = repo.get_template("failure_root_cause", "v2")
    
    assert t1.version == "v1"
    assert t2.version == "v2"
    assert t1.template_content != t2.template_content
