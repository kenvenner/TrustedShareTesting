# shell script to run the test in parallel
# run "./run.sh N" where N is the number of instances
# source venv/bin/activate is required if python virtual environment installed and configured
#!/bin/bash

for ARGUMENT in "$@"
do

    KEY=$(echo $ARGUMENT | cut -f1 -d=)
    VALUE=$(echo $ARGUMENT | cut -f2 -d=)

    case "$KEY" in
            instnum)  instnum=${VALUE} ;;
            tsfile)   tsfile=${VALUE} ;;
            url)      url=${VALUE} ;;
            pagecnt)  pagecnt=${VALUE} ;;
            pagewait)  pagewait=${VALUE} ;;
            findelementsloopcnt_pdfopen)  findelementsloopcnt_pdfopen=${VALUE} ;;
            findelementsloopcnt_nextpage)  findelementsloopcnt_nextpage=${VALUE} ;;
            utcstarttime)  utcstarttime=${VALUE} ;;
            startinmin)  startinmin=${VALUE} ;;
            browser)  browser=${VALUE} ;;
            *)
    esac


done

if [ -z "$instnum" ]; then instnum="1"
fi
if [ -z "$tsfile" ]; then tsfile_opt=""
else
  tsfile_opt="pagecnt=$tsfile"
fi
if [ -z "$url" ]; then url_opt=""
else
  url_opt="pagecnt=$url"
fi

if [ -z "$pagecnt" ]; then pagecnt_opt=""
else
  pagecnt_opt="pagecnt=$pagecnt"
fi
if [ -z "$pagewait" ]; then pagewait_opt=""
else
  pagewait_opt="pagewait=$pagewait"
fi
if [ -z "$findelementsloopcnt_pdfopen" ]; then findelementsloopcnt_pdfopen_opt=""
else
  findelementsloopcnt_pdfopen_opt="pagewait=$findelementsloopcnt_pdfopen"
fi
if [ -z "$pagefindelementsloopcnt_nextpagewait" ]; then findelementsloopcnt_nextpage_opt=""
else
  findelementsloopcnt_nextpage_opt="pagewait=$findelementsloopcnt_nextpage"
fi
if [ -z "$utcstarttime" ]; then utcstarttime_opt=""
else
  utcstarttime_opt="pagewait=$utcstarttime"
fi
if [ -z "$startinmin" ]; then startinmin_opt=""
else
  startinmin_opt="pagewait=$startinmin"
fi
if [ -z "$browser" ]; then browser_opt=""
else
  browser_opt="browser=$browser"
fi



source venv/bin/activate
for i in $(seq 1 $instnum)
do
  python ts_test.py $tsfile_opt $url_opt $pagecnt_opt $pagewait_opt $findelementsloopcnt_pdfopen_opt $findelementsloopcnt_nextpage_opt $utcstarttime_opt $startinmin_opt $browser_opt &
done

echo "Running scripts in parallel"
wait # This will wait until both scripts finish
echo "Script done running"
