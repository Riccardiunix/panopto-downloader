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

Scaricherà i primi 500 video dalla pagina "Subscription" del tuo account

	./panopto-downloader

Per scaricare video singoli si può usare il comando il comando:

	python panopto_url.py "URL"

e al termine di questo eseguire:

	sh output.sh

Nel formatto compatto:

	python panopto_url.py "URL";sh output.sh
