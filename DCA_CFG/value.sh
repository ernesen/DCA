#!/bin/sh

function copytoFile {
	for file in `ls *.csv` ; do
		echo "$file,no" | tee -a add.scv
	done
}

copytoFile