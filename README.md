# Document-analysis_API
This API assumes Annif as local server (by default http://127.0.0.1:5000). The client to this is an_tr_client.py.
Please use virtual enviroment of your choice. First install tika 
* https://computingforgeeks.com/how-to-install-apache-tika-on-ubuntu/?expand_article=1

  Install arkkiivi.txt (like requirements.txt)
  
  Place  nnrr2.py to your virtual enviroment. Follow the insctructions given by NER component
  
* Set your host and port, like
    
flask  --app ark run --host 101.251.36.10 -p 3001

Now, you should be good to go testing via postman

* Please note that english has limited support to NER, and swedish is not currently supported at all. On the other hand, annif works with these languages also.
