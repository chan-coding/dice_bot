import asyncio
from playwright.async_api import async_playwright
from app.config import settings
from app.dice import selectors
from app.utils import ensure_dir, ts

LOGIN_URL = "https://www.dice.com/dashboard/login"

async def login():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(LOGIN_URL)
        await page.fill(selectors.LOGIN_EMAIL, settings.DICE_EMAIL)
        await page.fill(selectors.LOGIN_PASSWORD, settings.DICE_PASSWORD)
        await page.click(selectors.LOGIN_BUTTON)

        # Give time for CAPTCHA/2FA manually
        await page.wait_for_timeout(8000)

        # Save session
        ensure_dir(".storage")
        await context.storage_state(path=settings.PLAYWRIGHT_STORAGE)
        await browser.close()

async def apply_to_job(job_url: str) -> str:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(storage_state=settings.PLAYWRIGHT_STORAGE)
        page = await context.new_page()
        await page.goto(job_url)

        btn = await page.query_selector(selectors.EASY_APPLY_BUTTON)
        if not btn:
            return "No Easy Apply button found (skipped)."

        await btn.click()
        await page.wait_for_timeout(1500)

        submit = await page.query_selector(selectors.APPLY_SUBMIT_BUTTON)
        if submit:
            await submit.click()
            await page.wait_for_timeout(1500)

        ensure_dir(settings.OUTPUT_DIR)
        shot = f"{settings.OUTPUT_DIR}/apply-{ts()}.png"
        await page.screenshot(path=shot, full_page=True)
        await browser.close()
        return f"Applied. Screenshot: {shot}"
