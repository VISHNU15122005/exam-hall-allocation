"""
End-to-end Playwright test covering: login -> upload -> preview -> confirm ->
generate allocation -> view seating -> search.

Requires: pip install playwright && playwright install, and the app running
on http://127.0.0.1:5000 (run `python run.py` in another terminal first), or
adapt to use Flask's live_server via pytest-flask if preferred.

Run:  pytest tests/integration/test_e2e_workflow.py
"""
import os
import pytest

playwright_sync = pytest.importorskip("playwright.sync_api")
from playwright.sync_api import sync_playwright

BASE_URL = os.environ.get("APP_BASE_URL", "http://127.0.0.1:5000")
SAMPLE_XLSX = os.path.join(os.path.dirname(__file__), "..", "..", "sample_data", "students.xlsx")


@pytest.fixture(scope="module")
def browser_page():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        yield page
        browser.close()


def test_full_upload_to_seating_workflow(browser_page):
    page = browser_page

    # 1. Login
    page.goto(f"{BASE_URL}/login")
    page.fill("input[name=username]", "admin")
    page.fill("input[name=password]", "admin123")
    page.click("button[type=submit]")
    assert "Dashboard" in page.content()

    # 2. Upload sample file
    page.goto(f"{BASE_URL}/imports/")
    page.set_input_files("input[type=file]", SAMPLE_XLSX)
    page.click("button[type=submit]")

    # 3. Preview shown, confirm import
    assert "Import Preview" in page.content()
    page.click("button:has-text('Confirm')")

    # 4. Go to exam sessions and generate allocation
    page.goto(f"{BASE_URL}/exams/")
    page.click("button:has-text('Generate Allocation')")

    # 5. Seating plan should render at least one filled seat
    assert page.locator(".seat-filled").count() > 0

    # 6. Student search
    page.goto(f"{BASE_URL}/search/?q=23CSE001")
    assert "23CSE001" in page.content()
