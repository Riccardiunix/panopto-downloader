import time
import pickle
import subprocess
from seleniumwire import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.action_chains import ActionChains

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

def has_audio(filename):
    cmd = "curl --silent {} | ffprobe -v error -show_entries format=nb_streams -of default=noprint_wrappers=1:nokey=1 pipe:0".format(filename)
    result = subprocess.run(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    return (int(result.stdout)-1)

def get_video_stream(video_url, driver):
    #-- Carico il nuovo video (in caso di timeout procedo con il prossimo)
    try:
        print("\nEsaminando: {}".format(video_url))
        driver.get(video_url)
    except:
        return ('', video_url)
    
    #-- Aspetto che la pagina carichi
    time.sleep(2)
    try:
        WebDriverWait(driver, 20).until( EC.presence_of_element_located(("id", "playButton")) )
        idPlay = "playButton"
    except Exception:
        WebDriverWait(driver, 10).until( EC.presence_of_element_located(("id", "playIcon")) )
        idPlay = "playIcon"
    
    #-- Ultimo stream prima del nuovo video
    del driver.requests

    time.sleep(1)

    try:
        #-- Riproduco il video un secondo per avere gli steam
        playButton = driver.find_element("id", idPlay)
        playButton.click()
        flagPlay = True
    except Exception:
        falgPlay = False
    
    try:
        #-- Premere sulle slide del tooltip
        driver.find_element("xpath", "/html/body/form/div[3]/div[9]/div[8]/main/div/ol/li[2]/img").click()
    except Exception:
        try:
            #-- Sposto avanti la barra di caricamente cosi' che appaino tutti gli eventuali stream
            bar = driver.find_element("id", "positionHandle")
            action = ActionChains(driver)
            action.move_to_element_with_offset(bar, 5, 6)
            action.click().perform()
        except Exception:
            pass

    #-- Prendo il nome della lezione
    if idPlay == "playIcon":
        driver.find_element("xpath", "/html/body/form/div[3]/div[10]/div[4]/div").click()
        driver.find_element("xpath", "/html/body/form/div[3]/div[9]/div/div/div[1]/div[3]/i").click()
        lec_name = driver.find_element("xpath", "/html/body/form/div[3]/div[9]/div/div/div[2]/div[3]/div/div[1]").text
    else:
        driver.find_element("id", "detailsTabHeader").click()
        lec_name = driver.find_element("xpath", "/html/body/form/div[3]/div[9]/div[8]/div/aside/div[2]/div[2]/div[2]/div[3]/div[1]").text
    print("Nome Lezione: {}".format(lec_name))
   
    #-- Prendo i link dello streaming video
    list_urls = []
    prev_len_url = 0
    flag = True # flag per il controllo di un solo flusso trovato, eseguo il controllo solo una volta
    for i in range(15):
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
        if len_set == 2:
            break
        elif flag and len_set == 1:
            test_url = list_urls[0] if list_urls[0][-1] != '/' else list_urls[0]+'00100.ts'
            if has_audio("'"+test_url+"'"):
                break
            flag = False
        time.sleep(2)
    
    output = ''
    error = ''
    if len_set == 1:
        print("1 flusso trovato [ok]")
        output = 'pdown {} "{}.mp4"\n'.format(list_urls[0], lec_name)
    elif len_set == 2:
        print("2 flussi trovati [ok]")
        output = 'pdown2 {} {} "{}.mp4"\n'.format(list_urls[0], list_urls[1], lec_name)
    else:
        print("{} flussi trovati [x]".format(len_set))
        error = '{} {}\n'.format(video_url, lec_name)
    return (output, error)

def get_lesson_links(driver, num_videos, url):
    #-- Accedo alla pagina e aspetto il suo caricamento
    print("Caricamento pagina del corso", end="", flush=True)

    driver.get("{}&maxResults={}".format(url, num_videos))
    
    #-- Accetto i 
    try:
        driver.find_element("id", "PageContentPlaceholder_loginControl_externalLoginButton").click()
    except Exception as e:
        pass

    try:
        WebDriverWait(driver, 15).until(EC.presence_of_element_located(("xpath","/html/body/form/div[3]/div[6]/div/div[1]/div[4]/div[1]/table[2]/tbody/tr[1]/td[2]/div/a")))
        n_div = 6
    except Exception:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located(("xpath","/html/body/form/div[3]/div[5]/div/div[1]/div[4]/div[1]/table[2]/tbody/tr[1]/td[2]/div/a")))
        n_div = 5
    print(" [ok]")
    
    print("Raccolta link delle lezioni", end="", flush=True)
    list_videos = []
    try:
        for video_id in range(1, num_videos):
            video_url = driver.find_element("xpath", "/html/body/form/div[3]/div[{}]/div/div[1]/div[4]/div[1]/table[2]/tbody/tr[{}]/td[2]/div/a".format(n_div, video_id))
            list_videos.append(video_url.get_attribute('href'))
    except:
        pass
    print(" [ok]")
    return list_videos

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
