import pickle
import time
import sys
from seleniumwire import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options

if len(sys.argv) == 1:
    print("Aggiungi almeno una URL del video che vuoi scaricare")

options = Options()
options.add_argument('--headless')
#options.add_argument('--no-sandbox')
#options.add_argument('--ignore-certificate-errors-spki-list')
#options.add_argument('--ignore-ssl-errors')
options.ignore_http_methods = [] # Capture all requests, including OPTIONS requests
options.page_load_strategy = 'eager' # non aspetto che venga caricata tutta la pagina ma solo che diventi iterativa (DOM caricato)
options.set_preference("media.volume_scale", "0.0") # muto l'audio

driver = webdriver.Firefox(options=options)

try:
    #-- Login (Cookies)
    cookies = pickle.load(open('cookies.pkl', 'rb'))
    driver.get('https://univr.cloud.panopto.eu')
    for cookie in cookies:
        driver.add_cookie(cookie)
except Exception:
    #-- Login (Username + Pass)
    driver.get("https://univr.cloud.panopto.eu/Panopto/Pages/Auth/Login.aspx?instance=AAP-Univr")
    WebDriverWait(driver, 30).until( EC.presence_of_element_located((By.ID, "form_username")) )
    driver.find_element("id", "form_username").send_keys("")
    driver.find_element("id", "form_password").send_keys("")
    driver.find_element("xpath", "/html/body/div[1]/div/div/div/div/div[1]/div[1]/form/div[3]/button/span[2]").submit()

output_file = open("output.sh", "w")
for url in sys.argv[1:]:
    #-- Carico il nuovo video (in caso di timeout procedo con il prossimo)
    try:
        driver.get(url)
    except:
        continue
    
    #-- Aspetto che la pagina carichi
    time.sleep(2)
    WebDriverWait(driver, 30).until( EC.presence_of_element_located((By.ID, "playButton")) )
    
    #-- Ultimo stream prima del nuovo video
    del driver.requests

    #-- Riproduco il video un secondo per avere gli steam
    playButton = driver.find_element("id", "playButton")
    playButton.click()
    
    try:
        #-- Sposto avanti la barra di caricamente cosi' che appaino tutti gli eventuali stream
        bar = driver.find_element("id", "positionHandle")
        action = ActionChains(driver)
        action.move_to_element_with_offset(bar, 5, 6)
        action.click().perform()
    except Exception:
        #-- Lascio riprodurre il video piu' allungo
        time.sleep(5)

    #-- Prendo il nome della lezione
    lec_name = driver.find_element("id", "deliveryTitle").text
    if lec_name == '':
        driver.find_element("id", "detailsTabHeader").click()
        lec_name = driver.find_element("xpath", "/html/body/form/div[3]/div[9]/div[8]/div/aside/div[2]/div[2]/div[2]/div[3]/div[1]").text
    
    #-- Se ho poche request aspetto
    if len(driver.requests) < 5: # se ho acquisito poche richieste aspetto ancora
        time.sleep(10)

    #-- Lascio riprodurre il video e poi lo fermo
    time.sleep(2)
    playButton.click()

    #-- Prendo i link dello streaming video
    list_urls = []
    prev_len_url = 0
    for i in range(len(driver.requests)-1, -1, -1):
        request = driver.requests[i]
        url = request.url
        len_url = len(url)
        if request.response and request.response.headers['Content-Type'] == 'video/mp4' and prev_len_url != len_url: # le URL degli stream devono avere lunghezza diversa
            list_urls.append(url)
            if prev_len_url != 0: # se ho gia' due stream (screen e webcam) mi fermo
                if len_url > prev_len_url:
                    list_urls = [list_urls[1], list_urls[0]]
                break
            prev_len_url = len_url
    
    len_set = len(list_urls)
    if len_set == 1:
        output = 'pdown {} "{}.mp4"\n'.format(list_urls[0], lec_name)
    elif len_set == 2:
        output = 'pdown2 {} {} "{}.mp4"\n'.format(list_urls[0], list_urls[1], lec_name)
    else:
        output = 'touch "{}"\n'.format(lec_name)

    #-- Output del programma
    output_file.write(output)

driver.quit()
output_file.close()
