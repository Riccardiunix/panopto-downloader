for file in *.ts; do 
  echo "file '$file'" >> file.lst 
done;

ffmpeg -f concat -i file.lst -c copy output.mp4 -y
rm file.lst

#unsilence -t 8 -ss 10 -stt 0.3 -y a.mp4 b.mp4
#rm a.mp4

#ffmpeg -i b.mp4 -c:v h264 -c:a libopus -crf 35 -filter:v fps=fps=10 $1 -y
#rm b.mp4
