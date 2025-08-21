# app/cli.py
import asyncio
import click
from app.dice.flows import login, apply_once
from app.utils import log

@click.group()
def cli():
    """Dice Bot CLI"""
    pass

@cli.command("login")
def login_cmd():
    """Login to Dice and save session cookies"""
    asyncio.run(login())

@cli.command("apply-url")
@click.argument("url")
def apply_url_cmd(url):
    """Apply to a single job by URL"""
    asyncio.run(apply_once(url))

if __name__ == "__main__":
    cli()
