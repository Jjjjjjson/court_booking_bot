import os
import time
from dotenv import load_dotenv
from datetime import datetime, timedelta

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Function to wait until a specific time (default 9:00:00)
def wait_until_target_time(hour, minute, second):
    now = datetime.now()
    target = now.replace(hour=hour, minute=minute, second=second, microsecond=0)

    if now >= target:
        print("Target time already passed for today.")
        return

    wait_seconds = (target - now).total_seconds()
    print(f"Current time: {now.strftime('%H:%M:%S')}")
    print(f"Waiting until: {target.strftime('%H:%M:%S')}")
    print(f"Sleeping for {wait_seconds:.1f} seconds...")
    time.sleep(wait_seconds)
    print("Target time reached.")

def select_date_7_days_later(driver, wait):
    target_date = datetime.now() + timedelta(days=7)
    target_day = str(target_date.day)

    print("Selecting date:", target_date.strftime("%Y-%m-%d"))

    time.sleep(2)

    # find visible date input
    inputs = driver.find_elements(By.TAG_NAME, "input")

    date_box = None
    for inp in inputs:
        value = (inp.get_attribute("value") or "").strip()
        if inp.is_displayed() and ("2026" in value or "Apr" in value or "April" in value):
            date_box = inp
            break

    if date_box is None:
        raise Exception("Could not find date box")

    # open date picker
    driver.execute_script("arguments[0].click();", date_box)
    print("Date picker opened.")

    time.sleep(1)

    # click target day
    day_button = wait.until(
        EC.element_to_be_clickable((
            By.XPATH,
            f"//button[normalize-space()='{target_day}']"
        ))
    )
    day_button.click()
    print(f"Selected day: {target_day}")

    # click Done
    done_button = wait.until(
        EC.element_to_be_clickable((
            By.XPATH,
            "//button[normalize-space()='Done']"
        ))
    )
    done_button.click()
    print("Date confirmed.")

def book_slot_by_index(driver, wait, time_text, court_number):
    slot_links = wait.until(
        EC.presence_of_all_elements_located((By.PARTIAL_LINK_TEXT, time_text))
    )

    print("Found matching slots:", len(slot_links))

    target_index = court_number - 1
    target_slot = slot_links[target_index]

    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", target_slot)
    time.sleep(0.5)
    target_slot.click()
    print(f"Clicked Court {court_number}, {time_text}")

    time.sleep(1)

    # Register button
    register_button = wait.until(
        EC.presence_of_element_located((
            By.XPATH,
            "//button[contains(., 'Register')]"
        ))
    )

    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", register_button)
    time.sleep(1)
    driver.execute_script("arguments[0].click();", register_button)

    print("Clicked Register.")

    # Select button
    time.sleep(2)
    select_button = wait.until(
        EC.presence_of_element_located((
            By.XPATH,
            "//button[contains(., 'Select')]"
        ))
    )
    driver.execute_script("arguments[0].click();", select_button)
    print("Clicked Select.")

    time.sleep(2)

    add_to_cart_button = wait.until(
        EC.presence_of_element_located((
            By.XPATH,
            "//button[contains(., 'Add to Cart')]"
        ))
    )
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", add_to_cart_button)
    time.sleep(0.5)
    driver.execute_script("arguments[0].click();", add_to_cart_button)
    print("Clicked Add to Cart.")

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

    # Click "Badminton - Courts"
    bookingCourts_button = wait.until(
        EC.element_to_be_clickable((
            By.PARTIAL_LINK_TEXT, "Badminton - Courts"
        ))
    )
    bookingCourts_button.click()
    print("Clicked Badminton - Courts.")

    # wait_until_target_time(15, 9, 0)
    # select_date_7_days_later(driver, wait)
    
    book_slot_by_index(driver, wait, "Apr 09 - 7:00 AM", 3) # Court 3, 7:00-8:00am on Apr 9

    input("Check result, then press Enter to close...")
    driver.quit()


if __name__ == "__main__":
    main()