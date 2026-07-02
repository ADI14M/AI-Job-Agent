# Demo Mode

The project comes with a fully automated Demonstration Mode that exercises the entire architecture without requiring human intervention, internet access, or complex LLM environments.

## Purpose
The `demo.sh` script validates the end-to-end architecture, verifying:
- Authentication & User creation
- Resume Parsing (Mocked)
- Job Discovery
- Decision Engine & Cover Letter Generation
- Career Memory Tracking
- Playwright Headless Automation

## Running the Demo

Ensure you have bash and python installed, then run from the root directory:
```bash
./demo.sh
```

### What happens?
1. **Cleanup**: Old demo databases (`demo.db`, `demo_chroma_db/`) are deleted.
2. **Boot**: FastAPI and Vite are spawned in the background on ports `8000` and `5173`.
3. **Execution**: The `demo.py` orchestration script runs sequentially through the application pipeline. It uses `IS_DEMO_MODE=True` to mock external API and LLM calls, ensuring 100% deterministic local tests.
4. **Reports**: Once complete, validation reports are written to the `reports/` folder.
5. **Teardown**: The background web servers are gracefully terminated.
