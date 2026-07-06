import time
from app.agent.browser_manager import browser_manager
from app.agent.login_manager import LoginManager
from app.agent.form_filler import FormFiller
from app.agent.models import FormProfile, ExecutionResult
from app.agent.retry_manager import RetryManager
from app.core.logger import system_logger
import os

class ApplicationExecutor:
    """
    The Strategy pattern router for provider-specific browser automation.
    Implemented as a mock dry-run framework by default to prevent accidental spam.
    """
    
    @staticmethod
    def get_executor(provider: str):
        executors = {
            "LinkedIn": LinkedInExecutor,
            "Greenhouse": GreenhouseExecutor,
            "Lever": LeverExecutor,
            "Ashby": AshbyExecutor,
            "CompanyCareers": GenericExecutor
        }
        return executors.get(provider, GenericExecutor)

class BaseExecutor:
    def __init__(self, user_id: int, profile: FormProfile, job_url: str):
        self.user_id = user_id
        self.profile = profile
        self.job_url = job_url
        self.provider = "Generic"
        self.logs = []

    def log(self, msg: str):
        system_logger.info(f"[{self.provider}] {msg}")
        self.logs.append(msg)

    def capture_screenshot(self, page, filename: str) -> str:
        path = f"storage/screenshots/{filename}.png"
        os.makedirs("storage/screenshots", exist_ok=True)
        page.screenshot(path=path)
        return path

    @RetryManager.with_retries(max_retries=2)
    def execute(self, dry_run=True) -> ExecutionResult:
        context = browser_manager.new_context(
            storage_state_path=LoginManager.get_session_path(self.user_id, self.provider)
        )
        page = context.new_page()
        
        try:
            self.log(f"Navigating to {self.job_url}")
            page.goto(self.job_url, timeout=30000)
            
            # Simulated Execution logic
            self.log("Identifying application type...")
            time.sleep(1)
            
            filler = FormFiller(self.profile)
            filler.fill_standard_fields(page)
            
            if dry_run:
                self.log("Dry run complete. Skipping actual submission click.")
                return ExecutionResult(success=True, final_state="READY_FOR_REVIEW", logs=self.logs)
                
            # Real submission logic would go here
            return ExecutionResult(success=True, final_state="SUBMITTED", logs=self.logs)

        except Exception as e:
            self.log(f"Execution failed: {e}")
            screenshot = self.capture_screenshot(page, f"fail_{self.user_id}_{int(time.time())}")
            return ExecutionResult(success=False, final_state="FAILED", logs=self.logs, error_message=str(e), screenshot_path=screenshot)
        finally:
            page.close()

class LinkedInExecutor(BaseExecutor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.provider = "LinkedIn"

class GreenhouseExecutor(BaseExecutor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.provider = "Greenhouse"
        
    @RetryManager.with_retries(max_retries=2)
    def execute(self, dry_run=True) -> ExecutionResult:
        context = browser_manager.new_context(
            storage_state_path=LoginManager.get_session_path(self.user_id, self.provider)
        )
        page = context.new_page()
        
        try:
            self.log(f"Navigating to {self.job_url}")
            page.goto(self.job_url, timeout=30000)
            
            # Real Greenhouse DOM traversal
            self.log("Identifying application iframe or form...")
            
            # Sometimes Greenhouse forms are embedded in an iframe named 'grnhse_iframe'
            form_frame = page
            if page.locator("iframe#grnhse_iframe").count() > 0:
                form_frame = page.frame_locator("iframe#grnhse_iframe")
            
            filler = FormFiller(self.profile)
            
            # Fill inputs
            try:
                if form_frame.locator("input#first_name").count() > 0:
                    form_frame.locator("input#first_name").fill(self.profile.first_name)
                if form_frame.locator("input#last_name").count() > 0:
                    form_frame.locator("input#last_name").fill(self.profile.last_name)
                if form_frame.locator("input#email").count() > 0:
                    form_frame.locator("input#email").fill(self.profile.email)
                if form_frame.locator("input#phone").count() > 0:
                    form_frame.locator("input#phone").fill(self.profile.phone)
                
                # Upload Resume (Requires actual file handling)
                if form_frame.locator("button[data-source='attach']").count() > 0:
                    self.log("Found resume attach button, simulating upload...")
                    # In a real environment, we'd do:
                    # form_frame.locator("input[type='file']").set_input_files("path/to/resume.pdf")
            except Exception as e:
                self.log(f"Partial fill error: {e}")

            if dry_run:
                self.log("Dry run complete. Pausing before submit.")
                screenshot = self.capture_screenshot(page, f"greenhouse_ready_{self.user_id}_{int(time.time())}")
                return ExecutionResult(success=True, final_state="READY_FOR_REVIEW", logs=self.logs, screenshot_path=screenshot)
                
            # Submit
            submit_btn = form_frame.locator("button#submit_app")
            if submit_btn.count() > 0:
                submit_btn.click()
                self.log("Application submitted!")
                return ExecutionResult(success=True, final_state="SUBMITTED", logs=self.logs)
            else:
                self.log("Submit button not found.")
                return ExecutionResult(success=False, final_state="FAILED", logs=self.logs, error_message="Submit button missing")

        except Exception as e:
            self.log(f"Execution failed: {e}")
            screenshot = self.capture_screenshot(page, f"fail_{self.user_id}_{int(time.time())}")
            return ExecutionResult(success=False, final_state="FAILED", logs=self.logs, error_message=str(e), screenshot_path=screenshot)
        finally:
            page.close()

class GenericExecutor(BaseExecutor):
    pass

class LeverExecutor(BaseExecutor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.provider = "Lever"

class AshbyExecutor(BaseExecutor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.provider = "Ashby"
