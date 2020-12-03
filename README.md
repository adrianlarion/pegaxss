
# Description: 
For each url make a number of requests equal to the number of payloads supplied multiplied by header rows supplied (if the headers are passid directly instead of a file then it counts as one row). During each request the specific payload is assigned to the headers in the header row. 

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
