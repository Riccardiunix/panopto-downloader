# panopto-downloader

## Prerequisiti

- python
- firefox (iceweasel)
- geckodriver
- wget
- ffmpeg
- parallel
- selenium
- selenium-wire

### Installazione prerequisiti

Sistema Operativi:

- Arch: `sudo pacman -S firefox geckodriver python wget ffmpeg parallel --needed`
- Parabola: `sudo pacman -S iceweasel geckodriver python wget ffmpeg parallel --needed`

Python: `pip install selenium selenium-wire`

## Installazione
Per installare gli script si può usare il seguente comando.

	sh install.sh

O copiare manualmente i file `downloader`, `joiner`, `pdown`, `pdown2` all'interno di una cartella di sistema (`$HOME/.local/bin` (script default), `/url/local/bin`).

Se utilizzate un fork di Firefox come Iceweasel è possibile che dobbiate creare un altro link simbolico, in questo modo:

	ln -s /bin/iceweasel /bin/firefox

## Configurazione

Per il primo utilizzo creare una file `login` (senza estensioni) con all'interno una linea per l'ID dell'account e un'altra per la password.

Esempio:

	ID007MIT
	NicePasswordBro

## Utilizzo

Ogni script python (`.py`) genererà un file `output.sh` con i comandi per scaricare i video trovati e un file `error_url` dove sono indicati i video di cui non è stato possibile trovati stream audio/video. Una volta concluso il `.py` si può procedere a eseguire il `output.sh` che scaricherà le lezioni.

I file python sono di tre tipi:

- **panopto_cor.py**: richiede come parametro la URL di un corso e scaricherà i primi `num_videos`(500) di quel corso
- **panopto_con.py**: scarica i primi `num_videos`(500) dalla pagina "Condiviso con me"
- **panopto_url.py**: richiede come paramento almeno una URL di un video che verrà poi scaricato.

### Esempi

Analizzare un corso:

	panopto_cor.py 'URL del corso'

Analizzare dalla pagina "Subscriptions"

	panopto_con.py

Analizzare video da URL
	
	panopto_url.py "URL1" "URL2" ... "URLn"

Scaricare le lezione analizzate dagli script python:
	
	sh output.sh

## Funzionamento

I file `.py` effettuano il login su panopto (via cookie o credenziali). Dopo di questo (per cor e con) va prendere tutti i link dei video nella pagina.

Ognuno di questi link viene poi analizzato per estrarre le request che la pagina fa verso panopto. Dalle request vengono poi estratte solo quelle che portano un flusso `video/mp4` o `video/MP2T`. Queste request andranno poi a formare il file output.sh dove avvera' il download effettivo.

La parte di estrazione delle request è la più delicata in quanto è quella che pregiudica il download o no della lezione. Spesso quando non funziona è dovuto a un tempo troppo lungo di caricamento o a request mandate e non risposte da parte di Panopto che per questo motivo non sono trovate da `selenium-wire`.

E possibile ritentare il download della lezione non scaricata con `panopto_url.py`.

Tutte le lezioni di cui non si hanno avuto request e quindi non scaricabili sono nel file `error_url`. 

## Note

Se avete problemi ad autenticarvi dopo un periodo in cui non aveva usato gli script probabilmente sarà necessario cancellare il file `cookie.pkl` in quanto i cookie salvati all'interno sono scaduti.

Per scaricare tutti i video di un corso o dalla pagina "Condiviso con me" è possibile settare `num_videos` a un valore molto alto (500-1000).

Una volta concluso lo script `.py` e necessario eseguire `output.sh` per eseguire effettivamente il download delle lezioni.

Per gli utenti Windows il modo piu' facile per usare gli script e' usando [Linux Mint](https://linuxmint.com/) alternativamente si può' usare [WSL](https://docs.microsoft.com/en-us/windows/wsl/install).

## Problemi noti (non funzionali)

L'output della esecuzione di `output.sh` presenta dei problemi di visualizzazione dovuto al programma `parallel` quando si scaricano flussi `.ts`, tuttavia non pregiudica il funzionamento del programma. Mostra righe di questo tipo:

	parallel: This job failed:
	wget URL/xxxxx.ts -q
	parallel: Starting no more jobs. Waiting for 1 jobs to finish.

Questo output è atteso e sta a significare che ha scaricato gli ultimi file del flusso e che deve attendere il completamento di altri.