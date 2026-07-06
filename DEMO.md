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

### What Does the Core System Do?
1. **Real ATS Discovery**: Scrapes Greenhouse, Lever, and Ashby JSON APIs directly using target company lists.
2. **Real Decision Engine**: Embeds job descriptions with local Ollama embeddings into ChromaDB, followed by an LLM secondary re-ranking pass.
3. **Application Automation**: Uses Playwright to traverse actual ATS DOM trees, map UserProfiles to inputs, and execute real submissions.
