import os
import time
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def main():
    load_dotenv()

    email = os.getenv("RA_EMAIL")
    password = os.getenv("RA_PASSWORD")

    if not email or not password:
        raise ValueError("Missing RA_EMAIL or RA_PASSWORD in .env")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    wait = WebDriverWait(driver, 30)

    driver.maximize_window()
    driver.get("https://www.racentre.com/playra.html")
    print("RA Centre opened successfully.")

    search_button = wait.until(
        EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "SEARCH"))
    )
    search_button.click()
    print("Search or Register button clicked.")

    time.sleep(3)

    if len(driver.window_handles) > 1:
        driver.switch_to.window(driver.window_handles[-1])
        print("Switched to new window.")

    wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

    print("Current URL:", driver.current_url)
    print("Title:", driver.title)

    # switch into iframe
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    print("iframe count:", len(iframes))
    if len(iframes) > 0:
        driver.switch_to.frame(iframes[0])
        print("Switched into first iframe.")

    email_input = wait.until(
        EC.presence_of_element_located((
            By.NAME,
            "j_id0:j_id5:loginComponent:loginForm:username"
        ))
    )

    password_input = wait.until(
        EC.presence_of_element_located((
            By.NAME,
            "j_id0:j_id5:loginComponent:loginForm:password"
        ))
    )

    login_button = wait.until(
        EC.element_to_be_clickable((
            By.NAME,
            "j_id0:j_id5:loginComponent:loginForm:loginButton"
        ))
    )

    email_input.clear()
    email_input.send_keys(email)

    password_input.clear()
    password_input.send_keys(password)

    print("Email and password entered successfully.")

    login_button.click()
    print("Login submitted.")

    # wait for dashboard
    wait.until(lambda d: "dashboard" in d.current_url.lower())
    print("Dashboard loaded.")

    time.sleep(2)
    driver.switch_to.default_content()

    # Top-left menu button
    menu_button = wait.until(
        EC.element_to_be_clickable((
            By.XPATH,
            "//*[name()='svg' or @role='button' or self::button][ancestor-or-self::*[position()]]"
        ))
    )

    menu_button.click()
    print("Menu opened.")

    time.sleep(1)

    # Click "Bookings & Registrations"
    booking_button = wait.until(
        EC.element_to_be_clickable((
            By.XPATH,
            "//span[contains(text(),'Bookings') or contains(text(),'Registrations')]"
        ))
    )
    booking_button.click()

    print("Clicked Bookings & Registrations.")

    input("Check result, then press Enter to close...")
    driver.quit()


if __name__ == "__main__":
    main()