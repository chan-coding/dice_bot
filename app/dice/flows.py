from playwright.async_api import async_playwright, TimeoutError as PWTimeout
from app.config import settings
from app.dice import selectors
from app.utils import ensure_dir, ts

LOGIN_URL = "https://www.dice.com/dashboard/login"

async def login():
    if not settings.DICE_EMAIL or not settings.DICE_PASSWORD:
        raise RuntimeError("DICE_EMAIL or DICE_PASSWORD is empty. Fill your .env and try again.")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto(LOGIN_URL)
        await page.wait_for_load_state("domcontentloaded")

        # --- Step 1: email / username ---
        await page.wait_for_selector(selectors.LOGIN_EMAIL, timeout=12000)
        await page.fill(selectors.LOGIN_EMAIL, settings.DICE_EMAIL)

        cont = await page.query_selector(selectors.CONTINUE_BUTTON)
        if cont:
            await cont.click()

        # --- Step 2: password (if shown) ---
        try:
            await page.wait_for_selector(selectors.LOGIN_PASSWORD, timeout=12000)
            await page.fill(selectors.LOGIN_PASSWORD, settings.DICE_PASSWORD)
        except PWTimeout:
            # Might already be logged in or redirected
            pass

        # If already logged in, save session and exit
        if (
            "home-feed" in page.url
            or "dashboard" in page.url
            or await page.query_selector(selectors.PROFILE_INDICATORS)
        ):
            ensure_dir(".storage")
            await context.storage_state(path=settings.PLAYWRIGHT_STORAGE)
            await browser.close()
            return

        # Submit only within form context
        submit_loc = page.locator(selectors.LOGIN_BUTTON).first
        if await submit_loc.count() > 0:
            await submit_loc.click()
        else:
            await page.keyboard.press("Enter")

        # Allow CAPTCHA/2FA/manual steps
        await page.wait_for_timeout(8000)

        # Success check
        if (
            "home-feed" in page.url
            or "dashboard" in page.url
            or await page.query_selector(selectors.PROFILE_INDICATORS)
        ):
            ensure_dir(".storage")
            await context.storage_state(path=settings.PLAYWRIGHT_STORAGE)
            await browser.close()
            return

        # Fallback: capture screenshot
        ensure_dir(".out")
        shot = f".out/login-failure-{ts()}.png"
        await page.screenshot(path=shot, full_page=True)
        await browser.close()
        raise RuntimeError(f"Login may have failed. Saved screenshot at {shot}")

async def apply_to_job(job_url: str) -> str:
    """Open a job URL, click Easy Apply if available, submit, and screenshot."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(storage_state=settings.PLAYWRIGHT_STORAGE)
        page = await context.new_page()
        await page.goto(job_url)
        await page.wait_for_load_state("domcontentloaded")

        btn = await page.query_selector(selectors.EASY_APPLY_BUTTON)
        if not btn:
            await browser.close()
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
