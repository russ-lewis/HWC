#! /bin/bash
#!/usr/bin/python

if [[ $* == "" ]]
then
  search=testcode/
else
  search=$*
fi

for TESTCASE in $(find $search -name *.wire 2>/dev/null | grep -v test_out | grep -v FAIL)
do

  base=$(echo $TESTCASE | rev | cut -f2- -d'.' | rev)

  {
    if [[ ! -f $base.csv ]]
    then
      python sim_main.py --wire $base.wire --auto
    else
      python sim_main.py --wire $base.wire --input $base.csv --auto
    fi

    rc=$?

    echo
    echo rc=$rc
  } > $base.stdout 2>&1

  echo "Testcase: $base.stdout created"

done