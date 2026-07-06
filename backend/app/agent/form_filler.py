from app.agent.models import FormProfile
from app.agent.question_answering import QuestionAnswering
from app.core.logger import system_logger

class FormFiller:
    """
    Maps DOM input elements to the FormProfile.
    """
    def __init__(self, profile: FormProfile):
        self.profile = profile

    def fill_standard_fields(self, page):
        """
        A heuristic-based method to fill standard known fields (Mock implementation).
        In a real scenario, this would use AI vision or robust CSS selectors.
        """
        system_logger.info(f"Filling standard form fields for {self.profile.email}")
        
        # Example pseudo-Playwright logic
        try:
            if page.locator("input[name*='first']").count() > 0:
                page.locator("input[name*='first']").fill(self.profile.first_name)
            if page.locator("input[name*='last']").count() > 0:
                page.locator("input[name*='last']").fill(self.profile.last_name)
            if page.locator("input[name*='email']").count() > 0:
                page.locator("input[name*='email']").fill(self.profile.email)
            if page.locator("input[name*='phone']").count() > 0:
                page.locator("input[name*='phone']").fill(self.profile.phone)
        except Exception as e:
            system_logger.warning(f"Error filling standard fields: {e}")

    def handle_custom_question(self, question_text: str) -> str:
        qa = QuestionAnswering.answer_question(self.profile, question_text)
        if qa.requires_human_review:
            system_logger.warning(f"Low confidence on question: {question_text}. Requires review.")
            return "" # Leave blank or flag for human review
        return qa.answer
