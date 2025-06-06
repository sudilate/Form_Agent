from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def extract_form_fields(url: str):
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    driver.get(url)
    fields = driver.find_elements(By.CSS_SELECTOR, 'input, textarea, select')

    field_labels = []
    for field in fields:
        label = field.get_attribute("aria-label") or field.get_attribute("placeholder") or field.get_attribute("name")
        if label:
            field_labels.append(label.strip())

    driver.quit()
    return field_labels
