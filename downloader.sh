for i in $(seq 0 1000); do
		wget $1$(printf "%05d" $i).ts || exit 0;
done
