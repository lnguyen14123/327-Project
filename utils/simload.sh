(python3 main.py "host") &
for i in `seq 1 $1`
do 
    (python3 main.py "join") &
done