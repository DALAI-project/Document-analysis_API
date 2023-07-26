#!/usr/bin/env python3
"""Module for accessing Annif REST API"""

import requests
#import time 
#from PIL import Image
#import pytesseract
#from tika import parser  
#from tika  import detector

# TR adds
#import os
#from multilingual_pdf2text.pdf2text import PDF2Text
#from multilingual_pdf2text.models.document_model.document import Document
#import logging
#logging.basicConfig(level=logging.INFO)
#import csv


# End TR adds


# Default API base URL
#API_BASE = 'http://api.annif.org/v1/'
API_BASE ='http://127.0.0.1:5000/v1/'

#path_to_textfile = '/home/digitalia-tr/DALAI/ve/annif-venv'

class AnnifClient:
    """Client class for accessing Annif REST API"""

    def __init__(self, api_base=API_BASE):
        self.api_base = api_base

    @property
    def projects(self):
        """Get a list of projects available on the API endpoint"""
        req = requests.get(self.api_base + 'projects')
        req.raise_for_status()
        return req.json()['projects']

    def get_project(self, project_id):
        """Get a single project by project ID"""
        req = requests.get(self.api_base + 'projects/{}'.format(project_id))
        if req.status_code == 404:
            raise ValueError(req.json()['detail'])
        req.raise_for_status()
        return req.json()

    def suggest(self, project_id, text, limit=None, threshold=None):
        """Suggest subjects for a text (either a string or a file-like object)
        using a specified project and optional limit and/or threshold settings.
        """
        if not isinstance(text, str):
            text = text.read()

        payload = {'text': text}

        if limit is not None:
            payload['limit'] = limit

        if threshold is not None:
            payload['threshold'] = threshold

        url = self.api_base + 'projects/{}/suggest'.format(project_id)
        req = requests.post(url, data=payload)
        if req.status_code == 404:
            raise ValueError(req.json()['detail'])
        req.raise_for_status()
        return req.json()['results']

    def learn(self, project_id, documents):
        """Further train an existing project on a text with given subjects."""

        url = self.api_base + 'projects/{}/learn'.format(project_id)
        req = requests.post(url, json=documents)
        if req.status_code == 404:
            raise ValueError(req.json()['detail'])
        req.raise_for_status()
        return req

    analyze = suggest  # Alias for backwards compatibility

    def __str__(self):
        """Return a string representation of this object"""
        return "AnnifClient(api_base='{}')".format(self.api_base)




    #print("* Learning on a document")
    #documents = [
    #    {"subjects":
    #        [{"uri": "http://example.org/fox", "label": "fox"}],
    #    "text":
    #        "the quick brown fox"
    #    }
    #]
    #req = annif.learn(project_id='tfidf-fi', documents=documents)
    
