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

#-- Salvo i cookie
pickle.dump(driver.get_cookies(), open("cookies.pkl","wb"))

output_file = open("output.sh", "w")
error_url = open("error_url", "w")
for video_url in sys.argv[1:]:
    #-- prendo i stream video
    output, error = utils.get_video_stream(video_url, driver)
    
    #-- Output del programma
    output_file.write(output)
    error_url.write(error)

driver.quit()
output_file.close()
error_url.close()
