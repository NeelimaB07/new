import json
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

# Function to log in to Amazon
def amazon_login(driver, email, password):
    driver.get("https://www.amazon.in")
    
    try:
        # Click on sign-in
        driver.find_element(By.ID, "nav-link-accountList").click()
        
        # Enter email
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "ap_email"))
        )
        email_input.send_keys(email)
        driver.find_element(By.ID, "continue").click()
        
        # Enter password
        password_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "ap_password"))
        )
        password_input.send_keys(password)
        driver.find_element(By.ID, "signInSubmit").click()
    
    except Exception as e:
        print(f"Login failed: {e}")
        driver.quit()
        exit()

# Function to scrape product data
def scrape_category(driver, category_url):
    driver.get(category_url)
    
    data = []
    try:
        for _ in range(15):  # Limiting to 1500 products, 100 per page
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "zg-item-immersion"))
            )
            
            products = driver.find_elements(By.CLASS_NAME, "zg-item-immersion")
            
            for product in products:
                try:
                    product_data = {
                        "Product Name": product.find_element(By.CLASS_NAME, "p13n-sc-truncate-desktop-type2").text,
                        "Product Price": product.find_element(By.CLASS_NAME, "p13n-sc-price").text,
                        "Sale Discount": "N/A",  # Placeholder if not available
                        "Best Seller Rating": product.find_element(By.CLASS_NAME, "a-icon-alt").get_attribute("textContent"),
                        "Ship From": "N/A",  # Placeholder for unavailable fields
                        "Sold By": "N/A",
                        "Rating": "N/A",
                        "Product Description": "N/A",
                        "Number Bought in the Past Month": "N/A",
                        "Category Name": driver.find_element(By.CLASS_NAME, "zg_selected").text,
                        "All Available Images": []  # Placeholder
                    }

                    data.append(product_data)
                except NoSuchElementException:
                    continue

            # Go to the next page
            try:
                next_button = driver.find_element(By.CLASS_NAME, "a-last")
                if "a-disabled" in next_button.get_attribute("class"):
                    break
                next_button.click()
                time.sleep(2)  # Delay for loading
            except NoSuchElementException:
                break

    except TimeoutException:
        print("Timeout while scraping category")

    return data

# Main function
def main():
    # User credentials
    email = "your-email@example.com"
    password = "your-password"

    # Category URLs to scrape
    categories = [
        "https://www.amazon.in/gp/bestsellers/kitchen/ref=zg_bs_nav_kitchen_0",
        "https://www.amazon.in/gp/bestsellers/shoes/ref=zg_bs_nav_shoes_0",
        "https://www.amazon.in/gp/bestsellers/computers/ref=zg_bs_nav_computers_0",
        "https://www.amazon.in/gp/bestsellers/electronics/ref=zg_bs_nav_electronics_0",
        # Add other category URLs here
    ]

    # Setup Selenium WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()

    # Log in to Amazon
    amazon_login(driver, email, password)

    all_data = []

    for category_url in categories:
        print(f"Scraping category: {category_url}")
        category_data = scrape_category(driver, category_url)
        all_data.extend(category_data)

    # Save data to JSON
    with open("amazon_best_sellers.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)

    print("Scraping complete. Data saved to 'amazon_best_sellers.json'.")

    driver.quit()

if __name__ == "__main__":
    main()
