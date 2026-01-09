import concurrent.futures
import vertexai
from vertexai.generative_models import GenerativeModel
from google.api_core import exceptions


class VertexLLM:
    def __init__(
        self,
        project_id: str,
        location: str = "us-central1",
        model_name: str = "gemini-2.0-flash",
        timeout: int = 45,
    ):
        self.project_id = project_id
        self.location = location
        self.model_name = model_name
        self.timeout = timeout

        vertexai.init(project=project_id, location=location)
        self.model = GenerativeModel(model_name)

    def generate(self, prompt: str, temperature: float = 0.2, max_tokens: int = 512) -> str:
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(
                    self.model.generate_content,
                    prompt,
                    generation_config={
                        "temperature": temperature,
                        "max_output_tokens": max_tokens,
                    },
                )
                response = future.result(timeout=self.timeout)

        except concurrent.futures.TimeoutError:
            return "ERROR: Vertex AI request timed out."
        except exceptions.GoogleAPIError as exc:
            return f"ERROR: Vertex AI request failed: {exc}"

        return (response.text or "").strip()
