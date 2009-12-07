#usage: sh run.sh <host> <movie descriptor> <input dir> <output dir>
python makemovies.py $1 $2 $4
python makecustomers.py $1 $3 $4
python makeratings.py $1 $3 $4
python insertdata.py /usr/local/bin/nap.py $3 -t 10