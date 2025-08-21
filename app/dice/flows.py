# app/dice/flows.py
from pathlib import Path
from playwright.async_api import async_playwright, TimeoutError as PWTimeout
from app.config import settings
from app.utils import log, ensure_dir, ts
from app.dice import selectors

LOGIN_URL = "https://www.dice.com/dashboard/login"
HOME_HINTS = ("home-feed", "dashboard")

STORAGE_FILE = Path(settings.PLAYWRIGHT_STORAGE)
OUTPUT_DIR = settings.OUTPUT_DIR


async def login() -> None:
    """
    Logs in to Dice (two-step email->continue->password), verifies success,
    saves storage state to settings.PLAYWRIGHT_STORAGE, and closes the browser.
    """
    if not settings.DICE_EMAIL or not settings.DICE_PASSWORD:
        raise RuntimeError("DICE_EMAIL or DICE_PASSWORD is empty in .env")

    ensure_dir(".storage")

    log("Opening Dice login page...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=1200)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto(LOGIN_URL)
        await page.wait_for_load_state("domcontentloaded")

        # Step 1: email
        log("Filling email...")
        await page.wait_for_selector(selectors.LOGIN_EMAIL, timeout=30000)
        await page.fill(selectors.LOGIN_EMAIL, settings.DICE_EMAIL)
        await page.wait_for_timeout(1000)

        cont = await page.query_selector(selectors.CONTINUE_BUTTON)
        if cont:
            await cont.click()
        else:
            await page.keyboard.press("Enter")
        await page.wait_for_timeout(2000)

        # Step 2: password
        try:
            log("Waiting for password...")
            await page.wait_for_selector(selectors.LOGIN_PASSWORD, timeout=30000)
            await page.fill(selectors.LOGIN_PASSWORD, settings.DICE_PASSWORD)
            await page.wait_for_timeout(1000)
        except PWTimeout:
            log("Password field not shown (SSO or already logged).")

        # Submit
        submit = page.locator(selectors.LOGIN_BUTTON).first
        if await submit.count() > 0:
            await submit.click()
        else:
            await page.keyboard.press("Enter")

        # Allow captcha/2FA/manual redirect — be generous here
        log("Waiting up to 30s for dashboard/profile redirect...")
        try:
            await page.wait_for_selector(selectors.PROFILE_INDICATORS, timeout=30000)
            logged_in = True
        except PWTimeout:
            logged_in = any(h in (page.url or "") for h in HOME_HINTS)

        ensure_dir(OUTPUT_DIR)
        if not logged_in:
            shot = f"{OUTPUT_DIR}/login-failure-{ts()}.png"
            await page.screenshot(path=shot, full_page=True)
            await browser.close()
            raise RuntimeError(f"Login not confirmed. Screenshot: {shot}")

        # Save storage and close
        await context.storage_state(path=str(STORAGE_FILE))
        log(f"✅ Login verified. Session saved to {STORAGE_FILE}.")
        await browser.close()



async def apply_once(job_url: str) -> None:
    """
    Opens a job URL using saved session and attempts an Easy Apply flow.
    Handles multi-step (Continue/Next -> Submit).
    Always takes a screenshot to OUTPUT_DIR.
    """
    ensure_dir(OUTPUT_DIR)

    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=1200)
        # Load saved session if present
        if STORAGE_FILE.exists():
            context = await browser.new_context(storage_state=str(STORAGE_FILE))
        else:
            context = await browser.new_context()
            log("⚠️ No saved storage found; proceeding without session (may not see Easy Apply).")

        page = await context.new_page()
        log(f"Opening job page: {job_url}")
        await page.goto(job_url)
        await page.wait_for_load_state("domcontentloaded")

        # Light scroll to trigger lazy UI
        await page.mouse.wheel(0, 800)
        await page.wait_for_timeout(600)

        # Find the real Easy Apply button (avoid sidebar spans)
        easy_btn = None
        candidates = [
            "button:has-text('Easy apply')",
            "button:has-text('Easy Apply')",
        ]
        for sel in candidates:
            loc = page.locator(sel).first
            try:
                if await loc.count() > 0 and await loc.is_visible():
                    easy_btn = loc
                    break
            except Exception:
                pass

        if not easy_btn:
            shot = f"{OUTPUT_DIR}/no-easy-apply-{ts()}.png"
            await page.screenshot(path=shot, full_page=True)
            log(f"❌ No Easy Apply button found. Screenshot: {shot}")
            await browser.close()
            return

        log("✅ Easy Apply button found — clicking…")
        await easy_btn.click()

        # Wait for any step in the flow (modal, steps, submit)
        try:
            await page.wait_for_selector(
                "button:has-text('Submit Application'), "
                "button:has-text('Submit'), "
                "button:has-text('Continue'), "
                "button:has-text('Next')",
                timeout=20000,
            )
        except PWTimeout:
            shot = f"{OUTPUT_DIR}/apply-no-modal-{ts()}.png"
            await page.screenshot(path=shot, full_page=True)
            log(f"⚠️ No application modal/steps detected. Screenshot: {shot}")
            await browser.close()
            return

        # Optional: pick resume if a select is present
        try:
            resume_select = page.locator("select[name*='resume' i]").first
            if await resume_select.count() > 0 and await resume_select.is_visible():
                log("📄 Selecting default resume…")
                await resume_select.select_option(index=0)
                await page.wait_for_timeout(1000)
        except Exception:
            # Not critical
            pass

        # Multi-step loop: click Continue/Next until Submit appears or no progress
        for _ in range(6):
            submit_app = page.locator("button:has-text('Submit Application')").first
            submit_plain = page.locator("button:has-text('Submit')").first
            cont = page.locator("button:has-text('Continue')").first
            nxt = page.locator("button:has-text('Next')").first

            if await submit_app.count() > 0 and await submit_app.is_visible():
                log("🚀 Submitting final application (Submit Application)…")
                await submit_app.click()
                await page.wait_for_timeout(2500)
                break
            if await submit_plain.count() > 0 and await submit_plain.is_visible():
                log("🚀 Submitting final application (Submit)…")
                await submit_plain.click()
                await page.wait_for_timeout(2500)
                break

            progressed = False
            if await cont.count() > 0 and await cont.is_visible():
                log("➡️ Clicking Continue…")
                await cont.click()
                progressed = True
            elif await nxt.count() > 0 and await nxt.is_visible():
                log("➡️ Clicking Next…")
                await nxt.click()
                progressed = True

            await page.wait_for_timeout(1500)
            if not progressed:
                log("ℹ️ No more progress buttons visible.")
                break

        # Screenshot outcome
        shot = f"{OUTPUT_DIR}/apply-{ts()}.png"
        await page.screenshot(path=shot, full_page=True)
        log(f"📸 Saved screenshot: {shot}")

        # Persist any updated cookies
        await context.storage_state(path=str(STORAGE_FILE))
        await browser.close()
