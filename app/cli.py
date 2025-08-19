import asyncio
import typer
from app.store import db
from app.dice.flows import login as login_flow, apply_to_job

app = typer.Typer(help="Dice Easy Apply v1.0.0 CLI")

@app.command()
def initdb():
    """Initialize local SQLite database."""
    db.init_db()
    typer.echo("Database initialized.")

@app.command()
def login():
    """Login to Dice (solve CAPTCHA/2FA manually if prompted)."""
    asyncio.run(login_flow())
    typer.echo("Login flow completed.")

@app.command()
def apply_url(url: str):
    """Apply to a single Easy Apply job by URL."""
    msg = asyncio.run(apply_to_job(url))
    typer.echo(msg)

if __name__ == "__main__":
    app()
