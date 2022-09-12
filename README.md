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

O copiare manualmente i file downloader, joiner, pdown, pdown2 e creare un link simbolico a panopto-downloader all'interno di una cartella di sistema.

Se utilizzate un fork di Firefox come Iceweasel è possibile che dobbiate creare un altro link simbolico, in questo modo:

	ln -s /bin/iceweasel /bin/firefox

## Configurazione

Per il primo utilizzo creare una file "login" con all'interno una linea per l'ID dell'account e un'altra per la password.

Esempio:

	ID007MIT
	NicePassowrdBro

## Utilizzo

Ogni script python (`.py`) genererà un file `output.sh` con i comandi per scaricare i video trovati e un file `error_url` dove sono indicati i video di cui non sono stati trovati stream audio/video. Una volta concluso il `.py` si può procedere ad eseguire il `output.sh` che scaricherà le lezioni.

I file python sono di 3 tipi:

- **panopto_cor.py**: richiede come parametro la URL di un corso e scaricherà i primi `num_videos`(500) di quel corso
- **panopto_sub.py**: scarica i primi `num_videos`(500) dalla pagina "Subscriptions"
- **panopto_url.py**: richiede come paramento almeno una URL di un video che verrà poi scaricato.

### Esempi
Analizzare un corso:

	panopto_cor.py 'URL del corso'

Analizzare dalla pagina "Subscriptions"

	panopto_sub.py

Analizzare video da URL
	
	panopto_url.py "URL1" "URL2" ... "URLn"

Scaricare le lezione analizzate dagli script python:
	
	sh output.sh

### Note
Per scaricare tutti i video di un corso o dalla pagina "Subscriptions" e' possibile settare `num_videos` a un valore molto alto (500-1000).

Una volta concluso lo script `.py` e necessario eseguire `output.sh` per eseguire effettivamente il download delle lezioni.
