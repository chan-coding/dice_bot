from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DICE_EMAIL: str
    DICE_PASSWORD: str

    PLAYWRIGHT_STORAGE: str = ".storage/dice.json"
    RESUME_AZURE_PATH: str = "resumes/azure/my_azure_resume.pdf"

    GOOGLE_SHEETS_CRED: str | None = None
    GOOGLE_SHEETS_SHEET_NAME: str = "Dice_Applications"

    OUTPUT_DIR: str = ".out"
    DB_PATH: str = ".data/dice.sqlite"
    CSV_PATH: str = ".data/applications.csv"

    class Config:
        env_file = ".env"

settings = Settings()
