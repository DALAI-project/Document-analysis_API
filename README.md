# Document-analysis_API
This API assumes Annif as local server (by default http://127.0.0.1:5000). The client to this is an_tr_client.py.
Please use virtual enviroment of your choice. 

- First install Apache Tika
  - For Linux Ubuntu, installation instructions can be found for example [here](https://computingforgeeks.com/how-to-install-apache-tika-on-ubuntu/?expand_article=1).

- Install `arkkiivi.txt` using the command `pip install -r arkkiivi.txt`
  
- Place  `nnrr2.py` to your virtual enviroment. Follow the insctructions given by the named entity recognition (NER) component

- Set your host and port, like
    
`flask  --app ark run --host 101.251.36.10 -p 3001`

Now, you should be good to go testing via Postman

- Please note that English has limited support in NER, and Swedish is not currently supported at all. On the other hand, Annif supports both of these languages.
