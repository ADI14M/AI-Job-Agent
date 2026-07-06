from app.services.ai_service import ai_service
from app.agent.models import FormProfile, QAConfidence
from app.core.logger import system_logger
import json

class QuestionAnswering:
    """
    Uses Ollama to answer application-specific questions based purely on the user's FormProfile.
    Never invents information.
    """
    @staticmethod
    def answer_question(profile: FormProfile, question: str) -> QAConfidence:
        prompt = f"""
        You are an AI assistant helping to fill out a job application.
        Answer the following question using ONLY the provided User Profile.
        Do NOT invent information. If the answer is not in the profile, set requires_human_review=true.

        <USER_PROFILE>
        {profile.model_dump_json()}
        </USER_PROFILE>

        <QUESTION>
        {question}
        </QUESTION>
        """
        system_logger.info(f"Answering question: {question}")
        result = ai_service.generate_structured(prompt, QAConfidence)
        if not result:
            return QAConfidence(answer="", confidence_score=0, requires_human_review=True)
        return result
