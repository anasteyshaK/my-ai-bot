
import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

GRADIO_URL = os.getenv(
    "GRADIO_URL",
    "http://host.docker.internal:7860"
)

SELENOID_URL = os.getenv(
    "SELENOID_URL",
    "http://localhost:4444/wd/hub"
)


def test_open_gradio_app():
    options = Options()
    options.add_argument("--window-size=1440,900")

    driver = webdriver.Remote(
        command_executor=SELENOID_URL,
        options=options
    )

    try:
        driver.get(GRADIO_URL)

        WebDriverWait(driver, 30).until(
            lambda browser: "Allied Testing AI Assistant"
            in browser.page_source
        )

        assert "Allied Testing AI Assistant" in driver.page_source

    finally:
        driver.quit()
