import pickle
import core
num_videos = 500

#-- Login
driver = core.get_driver()

try:
    #-- Accedo e prendo i link dei video delle lezioni nella pagina
    list_videos = core.get_lesson_links(driver, num_videos, "https://univr.cloud.panopto.eu/Panopto/Pages/Sessions/List.aspx#isSharedWithMe=true")

    #-- Analizzo i link delle lezione per estrarre gli stream
    core.get_links_video(driver, list_videos)
except Exception as e:
    print(e)
finally:
    driver.quit()
