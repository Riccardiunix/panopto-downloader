import pickle
import core
import sys

if len(sys.argv) == 1:
    print("Aggiungi almeno una URL del video che vuoi scaricare")

#-- Login
driver = core.get_driver()

#-- Analizzo i link delle lezione per estrarre gli stream
core.get_links_video(driver, sys.argv[1:])

driver.quit()
