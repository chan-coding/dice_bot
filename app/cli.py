import typer
import asyncio
from app.dice.flows import login, apply_once

app = typer.Typer(help="Dice Easy Apply Bot CLI")


@app.command()
def login_cmd():
    """Login to Dice and save session (cookies & storage)."""
    asyncio.run(login())


@app.command("apply-url")
def apply_url(job_url: str):
    """Apply to a single job posting by URL (requires prior login)."""
    asyncio.run(apply_once(job_url))


if __name__ == "__main__":
    app()
