import pickle
import utils
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
num_videos = 500

#-- Login
driver = utils.get_driver()

#-- Accedo alla pagina "Subscriptions" e aspetto il suo caricamento
print("Carico pagina 'Subscriptions'", end="", flush=True)
driver.get("https://univr.cloud.panopto.eu/Panopto/Pages/Sessions/List.aspx#isSubscriptionsPage=true&maxResults={}".format(num_videos))
WebDriverWait(driver, 30).until( EC.presence_of_element_located(("xpath", "/html/body/form/div[3]/div[5]/div/div[1]/div[4]/div[1]/table[2]/tbody/tr[1]/td[2]/div/a")) )
print(" [ok]")

#-- Salvo i cookie
#pickle.dump(driver.get_cookies(), open("cookies.pkl","wb"))

#-- Prendo i link dei video delle lezioni nella pagina
list_videos = utils.get_lesson_links(driver, num_videos)

#-- Analizzo i link delle lezione per estrarre gli stream
utils.get_links_video(driver, list_videos)

driver.quit()
