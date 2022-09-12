import pickle
import time
import utils
import sys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

if len(sys.argv) == 1:
    print("Aggiungi almeno una URL del video che vuoi scaricare")

#-- get driver da utils.py
driver = utils.get_driver()

num_videos = 10

#-- Pagina "Subscriptions"
driver.get("{}&maxResults={}".format(sys.argv[1], num_videos))

#-- Aspetto il caricamento della pagina
WebDriverWait(driver, 30).until( EC.presence_of_element_located(("xpath", "/html/body/form/div[3]/div[5]/div/div[1]/div[4]/div[1]/table[2]/tbody/tr[1]/td[2]/div/a")) )

#-- Salvo i cookie
pickle.dump(driver.get_cookies(), open("cookies.pkl","wb"))

#-- Click video_id link nella pagina
list_videos = []
try:
    for video_id in range(1, num_videos):
        video_url = driver.find_element("xpath", "/html/body/form/div[3]/div[5]/div/div[1]/div[4]/div[1]/table[2]/tbody/tr[{}]/td[2]/div/a".format(video_id))
        list_videos.append(video_url.get_attribute('href'))
except:
    pass

output_file = open("output.sh", "w")
error_url = open("error_url", "w")
for video_url in list_videos:
    #-- prendo i stream video
    output, error = utils.get_video_stream(video_url, driver)
    
    #-- Output del programma
    output_file.write(output)
    error_url.write(error)

driver.quit()
output_file.close()
error_url.close()
