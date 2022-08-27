import pickle
import time
from seleniumwire import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options

options = Options()
options.add_argument('--headless')
#options.add_argument('--no-sandbox')
#options.add_argument('--ignore-certificate-errors-spki-list')
#options.add_argument('--ignore-ssl-errors')
options.page_load_strategy = 'eager' # non aspetto che venga caricata tutta la pagina ma solo che diventi iterativa (DOM caricato)

driver = webdriver.Firefox(options=options)
#driver.set_page_load_timeout(30)
try:
    #-- Login (Cookies)
    cookies = pickle.load(open('cookies.pkl', 'rb'))
    driver.get('https://univr.cloud.panopto.eu')
    for cookie in cookies:
        driver.add_cookie(cookie)
except Exception:
    #-- Login (Username + Pass)
    driver.get("https://univr.cloud.panopto.eu/Panopto/Pages/Auth/Login.aspx?instance=AAP-Univr")
    #element = WebDriverWait(driver, 30).until( EC.presence_of_element_located((By.ID, "form_username")) )
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
list_videos = []
for vid_id in range(1, 10): 
    list_videos.append(driver.find_element("xpath", "/html/body/form/div[3]/div[5]/div/div[1]/div[4]/div[1]/table[2]/tbody/tr[{}]/td[2]/div/a".format(vid_id)).get_attribute('href'))

set_urls = set()
for url in list_videos:
    #-- Carico il nuovo video (in caso di timeout procedo con il prossimo)
    try:
        driver.get(url)
    except:
        continue
    
    #-- Aspetto che la pagina carichi
    time.sleep(2)
    element = WebDriverWait(driver, 30).until( EC.presence_of_element_located((By.ID, "playButton")) )
    
    #-- Ultimo stream prima del nuovo video
    del driver.requests

    #-- Riproduco il video un secondo per avere gli steam
    playButton = driver.find_element("id", "playButton")
    playButton.click()
    
    try:
        #-- Sposto avanti la barra di caricamente cosi' che appaino tutti gli eventuali stream
        bar = driver.find_element("id", "positionHandle")
        action = ActionChains(driver)
        action.move_to_element_with_offset(bar, 5, 5)
        action.click().perform()
    except Exception:
        #-- Lascio riprodurre il video piu' allungo
        print("No Bar")
        time.sleep(3)

    #-- Prendo il nome della lezione
    lec_name = driver.find_element("id", "deliveryTitle").text
    if lec_name == '':
        driver.find_element("id", "detailsTabHeader").click()
        lec_name = driver.find_element("xpath", "/html/body/form/div[3]/div[9]/div[8]/div/aside/div[2]/div[2]/div[2]/div[3]/div[1]").text
    lec_name = lec_name.replace(' ', '_').replace("'", '')
	
    #-- Lascio riprodurre il video e poi lo fermo
    #time.sleep(2)
    playButton.click()

    #-- Prendo i link dello streaming video
    set_urls = set()
    prev_len_url = 0
    if len(driver.requests) < 5: # se ho acquisito poche richieste aspetto ancora
        time.sleep(5)
    print(len(driver.requests))
    for i in range(len(driver.requests)-1, -1, -1):
        request = driver.requests[i]
        if request.response and request.response.headers['Content-Type'] == 'video/mp4':
            url = request.url
            len_url = len(url) 
            if prev_len_url != len_url: # le URL degli stream devono avere lunghezza diversa
                set_urls.add(url)
                if prev_len_url != 0: # se ho gia' due stream audio (screen e webcam) mi fermo
                    i = 0
                prev_len_url = len_url
    
    len_set = len(set_urls)
    if len_set == 1:
        output = 'pdown {} {}.mp4'.format(set_urls.pop(), lec_name)
    elif len_set == 2:
        #-- Ordino le url (+ lungo e' webcam e - lungo e' lo schermo)
        list_urls = list(set_urls)
        screen = list_urls[0]
        webcam = list_urls[1]
        if (len(screen) > len(webcam)):
            sceen = list_urls[1]
            webcam = list_urls[0]
        output = 'pdown2 {} {} {}.mp4'.format(webcam, screen, lec_name)
        #output = 'mkdir -p ' + cur_name + ';cd ' + cur_name + ';pdown2 ' + webcam + ' ' + screen + ' ' + lec_name + '.mp4'
    else:
        output = str(list(set_urls))

    # Output del programma
    print(output)

driver.quit()
