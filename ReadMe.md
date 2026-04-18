# AI Job Hunter (Local LLM Edition)
An automated job search pipeline that scrapes AI Engineer roles and grades them using a local **Llama 3** instance.

### Tech Stack
- **Scraper:** JobSpy (LinkedIn, Indeed, Glassdoor)
- **AI Grading:** Ollama (Llama 3)
- **Database:** Google Sheets API
- **Language:** Python 3.14

### How it Works
1. Scrapes jobs from specified regions (e.g., Milan, Munich).
2. Sends the JD to a local LLM to score the match based on my C++ and CV background.
3. Automatically updates a Google Sheet for morning review.