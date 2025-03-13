import time
import pickle
import subprocess
from seleniumwire import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

def get_driver():
    print("Login",end="", flush=True)
    options = Options()
    options.add_argument('--headless')
    options.page_load_strategy = 'eager' # non aspetto che venga caricata tutta la pagina ma solo che diventi iterativa (DOM caricato)
    options.set_preference("media.volume_scale", "0.0") # muto l'audio
    driver = webdriver.Firefox(options=options)

    try:
        #-- Login (Cookies)
        cookies = pickle.load(open('cookies.pkl', 'rb'))
        driver.get('https://aap.univr.it/')
        for cookie in cookies:
            driver.add_cookie(cookie)
        driver.get("https://univr.cloud.panopto.eu/Panopto/Pages/Auth/Login.aspx?instance=AAP-Univr")
        WebDriverWait(driver, 10).until( EC.presence_of_element_located( ("id", "headerSearch")) )
    except:
        #-- Login (Username + Pass)
        try:
            login = open("login", "r")
        except:
            print(" [ko]")
            print("Create un file 'login' con all'interno su una riga l'ID e su un'altra la password del vostro account")
            exit(1)
        driver.get("https://univr.cloud.panopto.eu/Panopto/Pages/Auth/Login.aspx?instance=AAP-Univr")
        WebDriverWait(driver, 30).until( EC.presence_of_element_located( ("id", "form_username")) )
        driver.find_element("id", "form_username").send_keys(login.readline())
        driver.find_element("id", "form_password").send_keys(login.readline())
        driver.find_element(By.CSS_SELECTOR, ".btn").click()
        time.sleep(1)
        #-- Salvo i cookie
        pickle.dump(driver.get_cookies(), open("cookies.pkl","wb"))
        WebDriverWait(driver, 10).until( EC.presence_of_element_located( ("id", "headerSearch")) )
    print(" [ok]")
    return driver

def has_audio(filename):
    cmd = f"curl --silent {filename} | ffprobe -v error -show_entries format=nb_streams -of default=noprint_wrappers=1:nokey=1 pipe:0"
    try:
        result = subprocess.run(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        return (int(result.stdout[-1])-1)
    except:
        return(0)

def get_video_stream(video_url, driver):
    #-- Carico il nuovo video (in caso di timeout procedo con il prossimo)
    try:
        print(f"\nEsaminando: {video_url}")
        driver.get(video_url)
    except:
        return ('', video_url)

    #-- Ultimo stream prima del nuovo video
    del driver.requests

    #-- Aspetto che la pagina carichi
    time.sleep(5)
    try:
        WebDriverWait(driver, 20).until( EC.presence_of_element_located(("id", "playButton")) )
        idPlay = "playButton"
    except:
        WebDriverWait(driver, 15).until( EC.presence_of_element_located(("id", "playIcon")) )
        idPlay = "playIcon"

    time.sleep(2)

    try:
        #-- Riproduco il video un secondo per avere gli steam
        playButton = driver.find_element("id", idPlay)
        playButton.click()
    except:
        pass

    try:
        #-- Premere sulle slide del tooltip
        driver.find_element(By.CSS_SELECTOR, "#thumbnail9thumbnailList > img:nth-child(2)").click()
    except:
        try:
            #-- Sposto avanti la barra di caricamente cosi' che appaino tutti gli eventuali stream
            bar = driver.find_element("id", "positionHandle")
            action = ActionChains(driver)
            action.move_to_element_with_offset(bar, 5, 6)
            action.click().perform()
        except:
            pass

    #-- Prendo il nome della lezione
    if idPlay == "playIcon":
        driver.find_element(By.CSS_SELECTOR, ".arrow").click()
        driver.find_element("id", "infoTab").click()
        lec_name = driver.find_element(By.CSS_SELECTOR, ".information-title").text
    else:
        driver.find_element("id", "detailsTabHeader").click()
        lec_name = driver.find_element(By.CSS_SELECTOR, ".name").text
    lec_name = lec_name.replace("/","-").replace(":","")
    print(f"Nome Lezione: {lec_name}")

    #-- Prendo i link dello streaming video
    list_urls = []
    prev_len_url = 0
    len_set = 0
    flag = True # flag per il controllo di un solo flusso trovato, eseguo il controllo solo una volta
    for _ in range(30):
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
            elif not request.response and prev_len_url != len_url and '.mp4' in url:
                list_urls.append(url)
                if prev_len_url != 0: # se ho gia' due stream (screen e webcam) mi fermo
                    if len_url > prev_len_url:
                        list_urls = [list_urls[1], list_urls[0]]
                    break
                prev_len_url = len_url

        len_set = len(list_urls)
        if len_set == 2:
            break
        elif flag and len_set == 1:
            test_url = "'"+list_urls[0]+"'" if list_urls[0][-1] != '/' else "'"+list_urls[0]+"00100.ts'"
            if has_audio(test_url):
                break
            flag = False
        time.sleep(2)

    output = ''
    error = ''
    if len_set == 1:
        if flag:
            print("1 schermata trovata [ok]")
        else:
            print("1 schermata trovata [-]")
        output = f'pdown "{list_urls[0]}" "{lec_name}.mp4"\n'
    elif len_set == 2:
        print("2 schermate trovate [ok]")
        output = f'pdown2 "{list_urls[0]}" "{list_urls[1]}" "{lec_name}.mp4"\n'
    else:
        print(f"{len_set} flussi trovati [x]")
        error = f"{video_url} {lec_name}\n"
    return (output, error)

def get_lesson_links(driver, num_videos, url):
    #-- Accedo alla pagina e aspetto il suo caricamento
    print("Caricamento pagina del corso", end="", flush=True)

    driver.get(f"{url}&maxResults={num_videos}")

    #-- Accetto
    try:
        driver.find_element("id", "PageContentPlaceholder_loginControl_externalLoginButton").click()
    except:
        pass
    print(" [ok]")

    print("Raccolta link delle lezioni", end="", flush=True)
    WebDriverWait(driver, 15).until(EC.presence_of_element_located(("id", "listViewContainer")))
    time.sleep(3)

    print(" [ok]")

    return set( x.get_attribute('href') for x in driver.find_element("id", "listViewContainer").find_elements("xpath", "//a[contains(@href,'Viewer')]") )

def get_links_video(driver, list_videos):
    output_file = open("output.sh", "w")
    error_url = open("error_url", "w")
    output_file.write('mkdir -p Videolezioni;cd Videolezioni;export PATH="$HOME/.local/bin:$PATH"\n')
    for video_url in list_videos:
        #-- prendo gli stream audio/video
        output, error = get_video_stream(video_url, driver)

        #-- Output del programma
        output_file.write(output)
        error_url.write(error)
    output_file.close()
    error_url.close()
