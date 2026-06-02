# API Documentation

## Phase 1: Resume Intelligence

### `POST /api/v1/resume/upload`

**Description:**
Upload a PDF or DOCX resume, extract its text robustly, parse it into structured JSON using the chosen LLM provider, store semantic embeddings in ChromaDB, and save all metadata to PostgreSQL.

**Query Parameters:**
- `provider` (string, optional): The LLM provider to use for parsing. Defaults to `openai`. Supported: `openai`, `ollama`.

**Request Body (multipart/form-data):**
- `file`: The resume file (PDF or DOCX).

**Response (200 OK):**
```json
{
  "id": 1,
  "filename": "john_doe_resume.pdf",
  "created_at": "2026-06-02T10:00:00Z",
  "parsed_data": {
    "name": "John Doe",
    "email": "johndoe@email.com",
    "phone": "555-1234",
    "location": "New York, NY",
    "linkedin": "https://linkedin.com/in/johndoe",
    "github": "https://github.com/johndoe",
    "portfolio": null,
    "summary": "Experienced software engineer...",
    "skills": ["Python", "FastAPI", "Docker"],
    "education": [
      {
        "institution": "State University",
        "degree": "BS in Computer Science",
        "location": null,
        "start_date": "2016",
        "end_date": "2020",
        "gpa": "3.8"
      }
    ],
    "experience": [ ... ],
    "projects": [ ... ],
    "certifications": [],
    "achievements": []
  }
}
```

**Errors:**
- `400 Bad Request`: Invalid file format or parsing validation failed.
- `500 Internal Server Error`: Disk write error or unhandled processing exception.

---

## Phase 2: Job Description Intelligence

### `POST /api/v1/jobs/`

**Description:**
Submit a raw Job Description, parse it into structured data (skills, salary, responsibilities, etc.) using the chosen LLM provider, store semantic embeddings in ChromaDB, and save all metadata to PostgreSQL.

**Request Body (application/json):**
```json
{
  "raw_text": "Backend Engineer at TechCorp...",
  "apply_url": "https://techcorp.com/jobs/123",
  "provider": "openai"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "title": "Backend Engineer",
  "company": "TechCorp",
  "location": "Remote",
  "apply_url": "https://techcorp.com/jobs/123",
  "created_at": "2026-06-02T10:00:00Z",
  "parsed_data": {
    "title": "Backend Engineer",
    "company": "TechCorp",
    "location": "Remote",
    "employment_type": "Full-time",
    "salary": "$120k - $150k",
    "required_skills": ["Python", "FastAPI"],
    "preferred_skills": ["Docker", "Kubernetes"],
    "responsibilities": ["Build APIs"],
    "experience_requirements": "5+ years",
    "education_requirements": null,
    "keywords": ["Backend", "Python"]
  }
}
```

---

## Phase 3: Semantic Matching Engine

### `POST /api/v1/matching/`

**Description:**
Evaluates a specific Resume against a specific Job Description. It combines semantic similarity (Cosine Distance via Vector Embeddings) and LLM-based structured evaluation (Skills, Experience, Education, Keywords).

**Request Body (application/json):**
```json
{
  "resume_id": 1,
  "job_id": 1,
  "provider": "openai"
}
```

**Response (200 OK):**
```json
{
  "resume_id": 1,
  "job_id": 1,
  "final_match_score": 94.0,
  "score_breakdown": {
    "skill_match_score": 38.0,
    "experience_match_score": 20.0,
    "education_match_score": 10.0,
    "keyword_match_score": 14.0,
    "semantic_similarity_score": 12.0
  },
  "missing_skills": ["Docker"],
  "strength_areas": ["Python", "Machine Learning"],
  "weak_areas": ["Experience"],
  "keyword_coverage": 90.0,
  "ats_readiness": "High",
  "education_match": true,
  "experience_match": true
}
```

**Errors:**
- `404 Not Found`: If either the `resume_id` or `job_id` does not exist in PostgreSQL.
- `400 Bad Request`: If the LLM abstraction fails to parse the structured response.

---

## Phase 7: Cover Letter Engine

### `POST /api/v1/cover_letter/`

**Description:**
Generate a tailored cover letter using the candidate's Resume and target Job Description.

**Request Body (application/json):**
```json
{
  "resume_id": 1,
  "job_id": 1,
  "company_name": "TechCorp",
  "provider": "openai"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "resume_id": 1,
  "job_id": 1,
  "content": "Dear Hiring Manager at TechCorp...",
  "file_path": null,
  "created_at": "2026-06-02T10:00:00Z"
}
```
---

## Phase 6: Resume Optimization Engine

### `POST /api/v1/resume_optimizer/`

**Description:**
Generate an optimized Resume targeted at a specific role without fabricating experience. Evaluates the base resume and outputs an optimized version matching the standard Resume schema.

**Request Body (application/json):**
```json
{
  "base_resume_id": 1,
  "target_role": "AI Engineer",
  "provider": "openai"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "base_resume_id": 1,
  "target_role": "AI Engineer",
  "optimized_data": {
    "name": "Aditya M",
    "summary": "Optimized for AI Engineer..."
  },
  "file_path": null,
  "created_at": "2026-06-02T10:00:00Z"
}
```
---

## Phase 5: Skill Gap Engine

### `POST /api/v1/skill_gap/`

**Description:**
Compare a candidate's Resume with the target Job Description to identify all missing Skills, Technologies, Tools, and Certifications, classified by priority (Critical, Important, Optional).

**Request Body (application/json):**
```json
{
  "resume_id": 1,
  "job_id": 1,
  "provider": "openai"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "resume_id": 1,
  "job_id": 1,
  "report_data": {
    "missing_items": [
      {
        "name": "Docker",
        "priority": "Critical",
        "category": "Tool"
      }
    ]
  },
  "created_at": "2026-06-02T10:00:00Z"
}
```
---

## Phase 4: ATS Analysis Engine

### `POST /api/v1/ats/`

**Description:**
Analyze a Resume against strict ATS rules (Formatting, Action Verbs, Section Completeness, etc.). Can optionally take a Job ID to analyze in the context of a JD.

**Request Body (application/json):**
```json
{
  "resume_id": 1,
  "job_id": null,
  "provider": "openai"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "resume_id": 1,
  "job_id": null,
  "overall_score": 85.0,
  "breakdown": {
    "formatting_score": 18.0,
    "length_score": 10.0,
    "section_completeness_score": 15.0,
    "action_verbs_score": 17.0,
    "quantified_achievements_score": 25.0
  },
  "recommendations": [
    {
      "category": "Experience",
      "priority": "Critical",
      "suggestion": "Add experience section"
    }
  ],
  "created_at": "2026-06-02T10:00:00Z"
}
```
