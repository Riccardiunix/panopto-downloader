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

**Sistema Operativi**:

- Arch: `sudo pacman -S firefox geckodriver python python-pip wget ffmpeg parallel curl --needed`
- Parabola: `sudo pacman -S iceweasel geckodriver python python-pip wget ffmpeg parallel curl --needed`
- Fedora: `sudo dnf install firefox python python-pip wget ffmpeg parallel curl`
- Linux Mint: `sudo apt install firefox python-is-python3 python3-pip wget ffmpeg parallel curl`

**Python**: `pip install selenium selenium-wire`

### Geckodriver

Sistemi operativi come Fedora e Linux Mint che non hanno `geckodriver` nel loro repository possono usare `cargo` per installarlo (compilarlo):

	sudo cargo install geckodriver --root /usr/local

Oppure è sufficente scaricarlo da [GitHub](https://github.com/mozilla/geckodriver/releases) e copiare l'eseguibile in una cartella di $PATH (`/usr/local/bin`), ho creato questo script per fare questo in autonomia:
    
    ./install-geckodriver.sh

## Installazione
Per installare gli script si può usare il seguente comando.

	sh install.sh

O copiare manualmente i file `downloader`, `joiner`, `pdown`, `pdown2` all'interno di una cartella di sistema (`$HOME/.local/bin` (script default), `/usr/local/bin`).

Se utilizzate un fork di Firefox come Iceweasel è possibile che dobbiate creare un altro link simbolico, in questo modo:

	sudo ln -s /bin/iceweasel /bin/firefox

## Configurazione

Per il primo utilizzo creare una file `login` (senza estensioni) con all'interno una linea per l'ID dell'account e un'altra per la password.

Esempio:

	ID007MIT
	NicePasswordBro

## Utilizzo

Ogni script python (`.py`) genererà un file `output.sh` con i comandi per scaricare i video trovati e un file `error_url` dove vengono indicati i video di cui non è stato possibile trovare gli stream audio/video. Una volta concluso il `.py` si può procedere a eseguire `output.sh` che scaricherà le lezioni disponibili.

I file python sono di tre tipi:

- **panopto_cor.py**: richiede come parametro in ingresso l'URL di un corso di studi e scaricherà i primi `num_videos`(500) di quel corso scelto
- **panopto_con.py**: scarica i primi `num_videos`(500) dalla pagina "Condiviso con me"
- **panopto_url.py**: richiede come paramento in ingresso almeno un URL di una videolezione che verrà poi scaricata.

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

I file `.py` effettuano il login su panopto (via cookie o credenziali) per poi (nel caso di `panopto_cor.py` e `panopto_con.py`) andare a prendere tutti i link delle videolezioni presenti nella pagina.

Ognuno di questi link viene poi analizzato per estrarre le request che la pagina effettua a Panopto: da queste request vengono estratte solo quelle che portano un flusso `video/mp4` o `video/MP2T`; tali request andranno poi a formare il file `output.sh` dove averà il download effettivo di tutte le lezioni.

La parte di estrazione delle request è la più delicata in quanto è quella che determina l'effettivo download o meno della lezione. Spesso, quando non funziona il `.py` scelto, può essere dovuto a un tempo troppo lungo di caricamento o a eventuali request mandate e non risposte da parte di Panopto (per questo motivo non sono trovate da `selenium-wire`).

È possibile ritentare il download della lezione non scaricata con `panopto_url.py`.

Tutte le lezioni di cui non si hanno avuto request, quindi non scaricabili, sono nel file `error_url`. 

## Note

Se avete problemi con l'autenticazione dopo un periodo in cui non avete più usato alcuno script, molto probabilmente sarà necessario cancellare il file `cookies.pkl` in quanto i cookies salvati all'interno saranno scaduti.

Per scaricare tutti i video di un corso o dalla pagina "Condiviso con me" è possibile settare `num_videos` a un valore molto alto (500-1000).

Una volta concluso uno script `.py` è necessario eseguire `output.sh` per eseguire l'effettivo download delle lezioni richieste.

Per gli utenti Windows il modo più facile per usare gli script è usando [Linux Mint](https://linuxmint.com/) o in alternativa [WSL](https://docs.microsoft.com/en-us/windows/wsl/install).

## Problemi noti (non funzionali)

L'output dell'esecuzione di `output.sh` presenta dei problemi di visualizzazione dovuti al programma `parallel` durante lo scaricamento dei flussi `.ts`; tuttavia non pregiudica il funzionamento del programma. Mostra righe di questo tipo:

	parallel: This job failed:
	wget URL/xxxxx.ts -q
	parallel: Starting no more jobs. Waiting for 1 jobs to finish.

Questo output è atteso e sta a significare che ha scaricato gli ultimi file del flusso e che deve attendere il completamento di altri.
