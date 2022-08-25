import pickle
import time
from seleniumwire import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

driver = webdriver.Firefox()
try:
    #-- Login (Cookies)
    cookies = pickle.load(open("cookies.pkl", "rb"))
    driver.get("https://univr.cloud.panopto.eu")
    for cookie in cookies:
        driver.add_cookie(cookie)
except Exception:
    #-- Login (Username + Pass)
    driver.get("https://univr.cloud.panopto.eu/Panopto/Pages/Auth/Login.aspx?instance=AAP-Univr")
    driver.find_element("id", "form_username").send_keys("")
    driver.find_element("id", "form_password").send_keys("")
    driver.find_element("xpath", "/html/body/div[1]/div/div/div/div/div[1]/div[1]/form/div[3]/button/span[2]").submit()

#-- Pagina "Subscriptions"
driver.get("https://univr.cloud.panopto.eu/Panopto/Pages/Sessions/List.aspx#isSubscriptionsPage=true")

#-- Aspetto il caricamento della pagina
element = WebDriverWait(driver, 30).until(
	EC.presence_of_element_located((By.XPATH, "/html/body/form/div[3]/div[5]/div/div[1]/div[4]/div[1]/table[2]/tbody/tr[1]/td[2]/div/a"))
)

#-- Salvo i cookie
pickle.dump(driver.get_cookies(), open("cookies.pkl","wb"))

#-- Click video_id link nella pagina
#?? pareralizza ricerca link con Pool
video_id=7
url = driver.find_element("xpath", "/html/body/form/div[3]/div[5]/div/div[1]/div[4]/div[1]/table[2]/tbody/tr[{}]/td[2]/div/a".format(video_id)).get_attribute('href')
driver.get(url)

#-- Aspetto che la pagina carichi
time.sleep(3)

element = WebDriverWait(driver, 30).until(
    EC.presence_of_element_located((By.ID, "positionHandle"))
)

#-- Sposto avanti la barra di caricamente cosi' che appaino tutti gli eventuali stream
bar = driver.find_element("id", "positionHandle")
action = ActionChains(driver)
action.move_to_element_with_offset(bar, 5, 5)
action.click().perform()

#-- Riproduco il video un secondo per avere gli steam
driver.find_element("id", "playButton").click()
time.sleep(1)
driver.find_element("id", "playButton").click()

#-- Prendo il nome della lezione
lec_name = driver.find_element("id", "deliveryTitle").text.replace(' ', '_')
if len(lec_name) == 0:
    driver.find_element("id", "detailsTabHeader").click()
    lec_name = driver.find_element("xpath", "/html/body/form/div[3]/div[9]/div[8]/div/aside/div[2]/div[2]/div[2]/div[3]/div[1]").text.replace(' ', '_')

#-- Prendo i link dello streaming video
set_urls = set()
for request in driver.requests:
    if request.response and request.response.headers['Content-Type'] == 'video/mp4': 
        set_urls.add(request.url)

#driver.quit()

len_set = len(set_urls)
if len_set == 1:
    output = 'pdown ' + set_urls.pop() + ' ' + lec_name + '.mp4'
elif len_set == 2:
    # Ordino le url (+ lungo e' webcam e - lungo e' lo schermo)
    list_urls = list(set_urls)
    screen = list_urls[0]
    webcam = list_urls[1]
    if (len(screen) > len(webcam)):
        sceen = list_urls[1]
        webcam = list_urls[0]
    output = 'pdown2 ' + webcam + ' ' + screen + ' ' + lec_name + '.mp4'
else:
    print("Troppe URLs")
    print(set_urls)
    exit(1)

# Output del programma
print(output)
