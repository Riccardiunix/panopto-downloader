import time
import pickle
from seleniumwire import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options

def get_driver():
    print("Login",end="", flush=True)
    options = Options()
    options.add_argument('--headless')
    #options.add_argument('--no-sandbox')
    #options.add_argument('--ignore-certificate-errors-spki-list')
    #options.add_argument('--ignore-ssl-errors')
    #options.ignore_http_methods = [] # Capture all requests, including OPTIONS requests
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
        try:
            login = open("login", "r")
        except Exception:
            print("Create un file 'login' con all'interno su una riga l'ID e su un'altra la password del vostro account")
            exit(1)
        driver.get("https://univr.cloud.panopto.eu/Panopto/Pages/Auth/Login.aspx?instance=AAP-Univr")
        WebDriverWait(driver, 30).until( EC.presence_of_element_located( ("id", "form_username")) )
        driver.find_element("id", "form_username").send_keys(login.readline())
        driver.find_element("id", "form_password").send_keys(login.readline())
        driver.find_element("xpath", "/html/body/div[1]/div/div/div/div/div[1]/div[1]/form/div[3]/button").click()
        time.sleep(1)
        #-- Salvo i cookie
        pickle.dump(driver.get_cookies(), open("cookies.pkl","wb"))
    print(" [ok]")
    return driver

def get_video_stream(video_url, driver):
    #-- Carico il nuovo video (in caso di timeout procedo con il prossimo)
    try:
        driver.get(video_url)
        print("\nEsaminando: {}".format(video_url))
    except:
        return ([], '')
    
    #-- Aspetto che la pagina carichi
    time.sleep(2)
    try:
        WebDriverWait(driver, 15).until( EC.presence_of_element_located(("id", "playButton")) )
        idPlay = "playButton"
    except Exception:
        WebDriverWait(driver, 15).until( EC.presence_of_element_located(("id", "playIcon")) )
        idPlay = "playIcon"
    
    #-- Ultimo stream prima del nuovo video
    del driver.requests
    
    try:
        #-- Riproduco il video un secondo per avere gli steam
        playButton = driver.find_element("id", idPlay)
        playButton.click()
        flagPlay = True
    except Exception:
        falgPlay = False

    try:
        #-- Premere sulla prima slide del tooltip
        driver.find_element("xpath", "/html/body/form/div[3]/div[9]/div[8]/main/div/ol/li[1]/img").click()
    except Exception:
        try:
            #-- Sposto avanti la barra di caricamente cosi' che appaino tutti gli eventuali stream
            bar = driver.find_element("id", "positionHandle")
            action = ActionChains(driver)
            action.move_to_element_with_offset(bar, 5, 6)
            action.click().perform()
        except Exception:
            #-- Lascio riprodurre il video più allungo
            time.sleep(5)

    #-- Prendo il nome della lezione
    if idPlay == "playIcon":
        driver.find_element("xpath", "/html/body/form/div[3]/div[10]/div[4]/div").click()
        driver.find_element("xpath", "/html/body/form/div[3]/div[9]/div/div/div[1]/div[3]/i").click()
        lec_name = driver.find_element("xpath", "/html/body/form/div[3]/div[9]/div/div/div[2]/div[3]/div/div[1]").text
    else:
        lec_name = driver.find_element("id", "deliveryTitle").text
        if lec_name == '':
            driver.find_element("id", "detailsTabHeader").click()
            lec_name = driver.find_element("xpath", "/html/body/form/div[3]/div[9]/div[8]/div/aside/div[2]/div[2]/div[2]/div[3]/div[1]").text
    print("Nome Lezione: {}".format(lec_name))

    #-- Se ho poche request aspetto
    if len(driver.requests) < 2: # se ho acquisito poche richieste aspetto ancora
        time.sleep(5)

    #-- Lascio riprodurre il video e poi lo fermo
    if flagPlay and idPlay != "playIcon":
        time.sleep(2)
        playButton.click()

    #-- Prendo i link dello streaming video
    list_urls = []
    prev_len_url = 0
    for request in driver.iter_requests():
        url = request.url
        len_url = len(url)
        if request.response and request.response.headers['Content-Type'] in ('video/mp4', 'video/MP2T') and prev_len_url != len_url: # le URL degli stream devono avere lunghezza diversa
            if request.response.headers['Content-Type'] == "video/MP2T":
                url = url[0:-8]
            list_urls.append(url)
            if prev_len_url != 0: # se ho gia' due stream (screen e webcam) mi fermo
                if len_url > prev_len_url:
                    list_urls = [list_urls[1], list_urls[0]]
                break
            prev_len_url = len_url

    len_set = len(list_urls)
    output = ''
    error = ''
    if len_set == 1:
        print("1 flusso trovato [ok]")
        output = 'pdown {} "{}.mp4"\n'.format(list_urls[0], lec_name)
    elif len_set == 2:
        print("2 flussi trovati [ok]")
        output = 'pdown2 {} {} "{}.mp4"\n'.format(list_urls[0], list_urls[1], lec_name)
    else:
        print("{} flussi trovati [x]")
        error = '{} {}\n'.format(video_url, lec_name)
    return (output, error)

def get_lesson_links(driver, num_videos):
    print("Raccolta link delle lezioni", end="", flush=True)
    list_videos = []
    try:
        for video_id in range(1, num_videos):
            video_url = driver.find_element("xpath", "/html/body/form/div[3]/div[5]/div/div[1]/div[4]/div[1]/table[2]/tbody/tr[{}]/td[2]/div/a".format(video_id))
            list_videos.append(video_url.get_attribute('href'))
    except:
        pass
    print(" [ok]")
    return list_videos

def get_links_video(driver, list_videos):
    output_file = open("output.sh", "w")
    error_url = open("error_url", "w")
    for video_url in list_videos:
        #-- prendo gli stream audio/video
        output, error = get_video_stream(video_url, driver)
        
        #-- Output del programma
        output_file.write(output)
        error_url.write(error)
    output_file.close()
    error_url.close()
