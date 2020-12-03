
# Description: 
For each url make a number of requests equal to the number of payloads supplied multiplied by header rows supplied (if the headers are passid directly instead of a file then it counts as one row).



During each request the specific payload is assigned to the headers in the header row. 



All sent requests are saved in a local .json file (so you can grep them later for your reports, should the need arise).



I reccommend using xsshunter.com to generate your payloads.

```
For each URL:
  For each payload:
    For each header row:
      Assign payload to headers in current header row and perform request.
```

# Install 
```
git clone https://github.com/truffle-dog/pegaxss
cd pegaxss
pip install -r requirements.txt
```
Additionally add pegaxss.py to your .bashrc so you can use it system wide. You need to have a 'bin' folder in your home folder (or create another dir where you'd like to keep your executables and soft link it there).
```
ln -s $PWD/pegaxss.py ~/bin/pegaxss.py
```



# Example usage:

* for each url deliver payloads in the headers specified




`$ pegaxss.py urls.txt -p payloads.txt -H "Origin"`

* same as above but using stdin




`$ cat urls.txt | pegaxss.py -p payloads.txt -H "Origin"`

* for each url deliver payloads using header rows from file. Headers on each line should be separated by space, without quotes. 





`$ pegaxss.py urls.txt -p payloads.txt -H headers.txt`





Example: headers.txt



```
Origin
Origin Referer
```

* specify custom delay and concurency level (number of processes)




`$ pegaxss.py urls.txt -p payloads.txt -H "Origin" -d 1 3 -c 10`

* specify a custom file to save the details about sent requests (instead of the default file which is %s)





`$ pegaxss.py urls.txt -p payloads.txt -H "Origin" -l "custom_datafile.json"`

# Disclaimer
This tool was made for legal usage in bug bounty pentests. 
Use responsibly and at your own risk and on websites where you have permission. The author declines any responsibility for how this tool is used. 
