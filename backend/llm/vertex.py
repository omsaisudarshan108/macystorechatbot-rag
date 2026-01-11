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
            error_msg = str(exc)
            # If permission denied, return fallback answer based on context
            if "IAM_PERMISSION_DENIED" in error_msg or "403" in error_msg:
                return self._extract_context_fallback(prompt)
            return f"ERROR: Vertex AI request failed: {exc}"

        return (response.text or "").strip()

    def _extract_context_fallback(self, prompt: str) -> str:
        """
        Fallback for local development when Vertex AI credentials unavailable.
        Extracts and summarizes the context from the prompt.
        """
        # Extract sources section from prompt
        if "Sources:" in prompt and "Question:" in prompt:
            sources_start = prompt.find("Sources:")
            question_start = prompt.find("Question:")

            if sources_start != -1 and question_start != -1:
                sources = prompt[sources_start:question_start].strip()
                question = prompt[question_start:].replace("Question:", "").strip()

                # Return a simple context-based answer
                return (
                    f"Based on the available documentation:\n\n{sources}\n\n"
                    f"(Note: This is a fallback response. For AI-generated answers, "
                    f"please configure Google Cloud credentials.)"
                )

        return "Unable to generate response: Vertex AI credentials not configured for local development."
