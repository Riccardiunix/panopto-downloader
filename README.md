# panopto-downloader

## Usage
Go to the video you want to download, go to the **Web Developer Tools** element (Ctrl + Shift + i) then go to the **Network** tab and take the URL that sends file like '00035.ts'.

Now you can launch the *downloader.sh* with the URL that you take previously **WITHOUT the last 8 character (the ts file like 00035.ts) but WITH the / at the end**

    downloader.sh https://cloudfront.net/sessions/aaaaaaaaaaa/Bbbbbbbbbbbbb.hls/123456/

This will make download via wget every single .ts file that compose the video.

When the download has finished, run the *join_ts.sh* to join the .ts in a single mp4 file

    ./join_ts.sh
