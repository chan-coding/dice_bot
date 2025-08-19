from pydantic import BaseModel
from datetime import datetime

class ApplicationRecord(BaseModel):
    job_id: str
    title: str
    company: str
    location: str
    link: str
    applied_at: datetime
    status: str = "applied"
    simplified_jd: str
    resume_file: str
    screenshot_path: str
