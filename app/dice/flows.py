import asyncio
from playwright.async_api import async_playwright
from app.config import settings
from app.utils import log


async def login():
    """Login to Dice and save cookies/session into .storage/dice.json"""
    log("Opening Dice login page...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=1500)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto("https://www.dice.com/dashboard/login")

        log("Filling in email...")
        await page.fill("input[type='email']", settings.DICE_EMAIL)
        await page.click("button:has-text('Continue')")

        log("Waiting for password field...")
        await page.fill("input[type='password']", settings.DICE_PASSWORD)
        await page.click("button:has-text('Sign In')")

        # wait for profile/dashboard after login
        try:
            await page.wait_for_selector("text=Profile", timeout=30000)
            log("✅ Login verified, saving session...")
            await context.storage_state(path=settings.PLAYWRIGHT_STORAGE)
        except Exception:
            log("⚠️ Could not verify login automatically — please check manually in browser.")
            await asyncio.sleep(60)  # give user time to fix login manually
            await context.storage_state(path=settings.PLAYWRIGHT_STORAGE)

        await browser.close()
        log("Login flow completed. Storage saved.")


async def apply_once(job_url: str):
    """Apply to a job using stored login session"""
    log(f"Opening job page: {job_url}")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=1500)
        context = await browser.new_context(storage_state=settings.PLAYWRIGHT_STORAGE)
        page = await context.new_page()

        await page.goto(job_url)
        await page.wait_for_load_state("domcontentloaded")

        try:
            button = page.locator("button:has-text('Easy apply')").first
            if await button.is_visible():
                log("✅ Easy Apply button found — clicking...")
                await button.click()

                # Wait for modal
                await page.wait_for_selector("text=Submit Application", timeout=15000)

                # Resume dropdown if present
                try:
                    resume_select = page.locator("select[name='resume']")
                    if await resume_select.is_visible():
                        log("📄 Selecting default resume...")
                        await resume_select.select_option(index=0)
                except:
                    log("ℹ️ No resume selector found (maybe already selected).")

                # Submit
                log("🚀 Submitting application...")
                await page.locator("button:has-text('Submit Application')").click()

                await page.wait_for_timeout(5000)
                log("🎉 Application submitted (check manually to confirm).")

            else:
                log("⚠️ No Easy Apply button found (skipped).")

        except Exception as e:
            log(f"❌ Error: {e}")

        await browser.close()
