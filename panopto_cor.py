import pickle
import time
import utils
import sys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
num_videos = 500

if len(sys.argv) == 1:
    print("Aggiungi almeno una URL del video che vuoi scaricare")

#-- Login
driver = utils.get_driver()

#-- Accedo alla pagina del corso e aspetto il suo caricamento
print("Carico pagina del corso", end="", flush=True)
driver.get("{}&maxResults={}".format(sys.argv[1], num_videos))
WebDriverWait(driver, 30).until( EC.presence_of_element_located(("xpath", "/html/body/form/div[3]/div[5]/div/div[1]/div[4]/div[1]/table[2]/tbody/tr[1]/td[2]/div/a")) )
print(" [ok]")

#-- Salvo i cookie
#pickle.dump(driver.get_cookies(), open("cookies.pkl","wb"))

#-- Prendo i link dei video delle lezioni nella pagina
list_videos = utils.get_lesson_links(driver, num_videos)

#-- Analizzo i link delle lezione per estrarre gli stream
utils.get_links_video(driver, list_videos)

driver.quit()
