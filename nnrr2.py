import os
import time
import argparse
import spacy
from collections import defaultdict
from transformers import pipeline 


class NERextractor:
    """
    Class for extracting named entities from input documents.
    """
    def __init__(self):
        # Path to model page in HuggingFace
        self.checkpoint_path = "Kansallisarkisto/finbert-ner"
        self.fi_pipeline = self.load_pipeline()
        self.en_pipeline = spacy.load("en_core_web_trf", disable=["tagger", "parser", "attribute_ruler", "lemmatizer"])
        self.tag_list = ['PERSON','ORG','LOC','GPE','PRODUCT','EVENT','DATE','JON','FIBC','NORP']
        self.n = 100 # Default maximum length for single text input

    def load_pipeline(self):
        """
        Function for loading the model and tokenizer pipeline.
        """
        try:
            token_classifier = pipeline("token-classification", 
                                        model=self.checkpoint_path, 
                                        aggregation_strategy="first",
                                        framework="pt",
                                        device=-1)
        except Exception as e:
            print("Failed to load checkpoint files from HuggingFace: {}".format(e))

        return token_classifier


    def filter_tags(self, included_tags, predictions_list, language):
        """Filters out tags not included in the included_tags list."""
        predictions_dict = defaultdict(set)
        # If list for filtering tags is empty, all tags (except 'O') are included
        included_tags = self.tag_list if included_tags == [] else included_tags  
        # Keep only items with tags contained in the 'included_tags' list
        for item in predictions_list:
            if item['entity_group'] in included_tags:
                predictions_dict[item['entity_group']].add(item['word'])
        # FIBC and JON are not recognized by the Spacy NER model, so a disclaimer
        # is added to the output if they are selected for input in English
        if (language == 'en') and any(tag in included_tags for tag in ['JON', 'FIBC']):
            disclaimer = 'Entity is not available in English NER.'
            if 'JON' in included_tags:
                predictions_dict['JON'].add(disclaimer)
            if 'FIBC' in included_tags:
                predictions_dict['FIBC'].add(disclaimer)

        return predictions_dict

    def validate_input(self, input):
        """Checks that the keys and values of input dictionary exist and are of the right type."""
        # Set default values if dictionary key-value pairs are missing or of the wrong type
        input['lang'] = input['lang'] if 'lang' in input and input['lang'] in ['fi', 'en'] else 'fi'
        input['tag_filter'] = input['tag_filter'] if 'tag_filter' in input and isinstance(input['tag_filter'], list) else []
        input['text'] = input['text'] if 'text' in input and isinstance(input['text'], str) else ''
        input['length'] = len(input['text'].split())

        return input
    
    def get_predictions(self, lang, text):
        """Gets model predictions for a single text string.
        Based on the language of the input, either English or Finnish model is used."""
        if lang == 'fi':
            predictions_list = self.fi_pipeline(text)
        elif lang == 'en':
            predictions = self.en_pipeline(text)
            predictions_list = [{'entity_group': ent.label_, 'word': ent.text} for ent in predictions.ents]
        
        return predictions_list

    def split_text(self, input):
        """Splits text string into smaller chunks and gets predictions for 
        each chunk separately."""
        text_tokens = input['text'].split()
        split_texts = [' '.join(text_tokens[i:i + self.n]) for i in range(0, len(text_tokens), self.n)] 
        combined_preds = []
        lang = input['lang']
        # Loops over text list and gets predictions for each text chunk
        for text in split_texts:
            pred = self.get_predictions(lang, text)
            combined_preds += pred

        return combined_preds


    def predict(self, input):
        """Predicts NER tags for the input texts based on the language."""
        input = self.validate_input(input)
        # If input text length is > n, it is split into smaller chunks
        if input['length'] > self.n:
            predictions_list = self.split_text(input)
        else:
            predictions_list = self.get_predictions(input['lang'], input['text'])

        # Returns a dictionary with NER tags as keys and lists of tokens as values.
        # O-tag is not included in the results.
        predictions_dict = self.filter_tags(input['tag_filter'], predictions_list, input['lang'])

        return predictions_dict
        

#def main():