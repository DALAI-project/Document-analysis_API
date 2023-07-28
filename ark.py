#from msilib.schema import File
from argparse import Namespace
from code import interact
from html.parser import HTMLParser
from tkinter.ttk import Separator
from PIL import Image
from pytesseract import image_to_string
from pytesseract import image_to_data, Output
import time,os 
from tika import parser
from tika import language
import cv2
import metadalai as metadata
import dateparser
from flask import Flask,request, flash, redirect, url_for,jsonify
#from flask_api import status
from flask_cors import CORS
from werkzeug.utils import secure_filename
#import metas
from metadata import MetadataExtractor as mt 
import re
#import annif_cfg
import pandas as pd
#import lmdb



from multilingual_pdf2text.pdf2text import PDF2Text
from multilingual_pdf2text.models.document_model.document import Document

#Added import for multiprocessing
import multiprocessing
from multiprocessing import Pool
#import annif as an
from an_tr_client import AnnifClient
#import an_tr_client
import csv
import json
import ntpath

# Set input and output dir, default is rm to these files before return 
in_dir = r'/Input/'

out_dir = r'/Output/'

import nnrr2


nrr = nnrr2.NERextractor()
# For annif number of the subjects
Nsubjects = 10
NAnnifModels = 5 
# Default project for annif
an_proj = 'yso-fi'
#
app  = Flask(__name__)
CORS(app)

annif = AnnifClient()
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024
UPLOAD_FOLDER  = in_dir
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER 




@app.route('/upload/',methods = ['GET','POST'])
def upload_file(file):
	
	if request.method =='POST':
		
		if 'file' not in request.files:
			flash('No file part')
			return ' Ei filua '
		
		file = request.files['file']
		
		filename = file.filename
		
		file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))

		
	
	return str(filename)


def do_annif(input_filename, input_text, project_name,FileToWrite,outlist,inlist,idj):
	#print(' Annifiin ')
	y_tunnus = ' '
	diaari =' '
	tikafile = parser.from_buffer(input_text)
	
	
	
	con = tikafile['content']
	conn = list(con.split(' '))
	connn=[]
	# Removing \n, tabs etc....
	for sub in conn:
		connn.append(re.sub('-\n','',sub))
		
	c2 = []
	for sub in connn:
		c2.append(re.sub('\n',' ',sub))
		

	#con =  con.replace('\\n',' ')
	#cont = ' '.join(c2)
	c3 = []
	for sub in c2:
		c3.append(re.sub('\t',' ',sub))
		
	cont = ' '.join(c3)
	project_name='yso-fi'
	lang = language.from_buffer(cont)
	#print(conn)
	input_ner = {'text': cont, 'lang': lang, 'tag_filter': []}
	#print(input_ner['text'])
	predictions = nrr.predict(input_ner)
	if lang == 'en':
		project_name = 'yso-en'
	elif lang=='sv':
		project_name = 'yso-sv'

	out_goes = []
	s = ''
	inlist = json.loads(inlist)
	
	if inlist["annif"]== 1:
		results = annif.suggest(project_id=project_name,text= tikafile['content'], limit= Nsubjects)
	
	
		s = ','
		if len(input_text) == 1:
			outlist[2] = 'Yes'
		else:
			outlist[2] = 'No'
		for result in results:
			out_goes.append(result['label'])
		s=s.join(out_goes)     
#	print(s)
	outlist[3] = s
	if len(predictions['PERSON']) > 0 and inlist['name'] ==1: 
		outlist[2]= ', '.join(predictions['PERSON'])
	else:
		outlist[2]=[]

	if len(predictions['ORG'])> 0 and inlist['act']== 1:
		outlist[1] = ', '.join(predictions['ORG'])
		#outlist[1] = predictions['ORG']
	else:
		outlist[1] = []
	outlist[4]=lang
	
	if len(predictions['DATE']) >0 and inlist['date']== 1:
		pvm_std = ', '.join(predictions['DATE'])
	
	else:
		pvm_std=[]
		
	#outlist[5]= pvm_std

	if lang == 'fi':
		if len(predictions['FIBC']) >0 and inlist['y_field'] == 1:
			y_tunnus = ', '.join(predictions['FIBC'])
	
		else:
			y_tunnus=[]

	if lang == 'fi':
		if len(predictions['JON']) >0 and inlist['diar'] == 1 :
			diaari = ', '.join(predictions['JON'])
	#outlist[5] = str(type(outlist[5]))
		else:
			diaari=[]

	if len(predictions['LOC']) >0 and inlist['loc'] == 1:
		loc = ', '.join(predictions['LOC'])
		#print(' lokaatiot', loc)
	#outlist[5] = str(type(outlist[5]))
	else:
		loc=[]
		#print(' Ei lokaatiota ')


	sotu = []	

	#lang = language.from_buffer(tikafile['content'])

	#
	
	if len(predictions['GPE']) > 0 and inlist['gpe'] == 1:
		gpe = ', '.join(predictions['GPE'])
	else:
		gpe = []

	if len(predictions['PRODUCT'])>0 and inlist['product'] == 1:
		product = ', '.join(predictions['PRODUCT'])
	else:
		product = []

	
	if len(predictions['EVENT'])>0 and inlist['event'] == 1:
		event = ', '.join(predictions['EVENT'])
	else:
		event = []

	
	 
	if len(predictions['NORP'])>0 and inlist['norp'] == 1:
		norp = ', '.join(predictions['NORP'])
	else:
		norp = []
	

	outlist[4]=lang
	outlist[5]=pvm_std
	outlist[6]=y_tunnus
	outlist[7]=diaari
	outlist[8]= sotu
	outlist[9]= loc
	outlist[10]= gpe
	outlist[11] = product
	outlist[12] = event
	outlist[13] = norp
	outlist[14] = idj


	#outlist[9] = idj
	with open(FileToWrite, mode='w') as annif_out:
		annif_writer = csv.writer(annif_out, quotechar='"', delimiter=';',quoting=csv.QUOTE_MINIMAL)	
		annif_writer.writerow(outlist)
		annif_out.close()
	return  

def pdftoText(FileToRead,FileToWrite,outlist):
#    If OCR is needed
	#print( ' OCR ')
	pdf_document = Document(document_path=FileToRead, language='fin' )
	pdf2text = PDF2Text(document=pdf_document)
	content = pdf2text.extract()
	
	
	return content


#if __name__ == '__main__':
#	#annif = AnnifClient()
@app.route('/', methods=['GET', 'POST'])
def my_annif():
	
	an = int(request.args.get("annif"))
	#print(an)
	name_j = int(request.args.get('name'))
	act_j= int(request.args.get('act'))
	sos_j = int(request.args.get("sos"))
	y_field_j = int(request.args.get('y_field'))
	diar_j= int(request.args.get('diar'))
	date_j = int(request.args.get('date'))
	lg_j= int(request.args.get('lang'))
	loc_j= int(request.args.get('loc'))
	gpe_j= int(request.args.get('gpe'))
	product_j= int(request.args.get('product'))
	event_j= int(request.args.get('event'))
	norp_j= int(request.args.get('norp'))
	idj = str(request.args.get('id'))
	#idj = str(idj)
	print(idj)
	
	file = request.files['file']
	FileToRead = secure_filename(file.filename)
	filename = file.filename
	filename = secure_filename(file.filename)
	file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
	
	FileToRead = UPLOAD_FOLDER +  str(FileToRead)
	
	
	tlist=  {"annif":an,"name":name_j,"act":act_j,"sos":sos_j,"y_field":y_field_j,"diar":diar_j,"date":date_j,"lang":lg_j,"loc":loc_j,"gpe":gpe_j,"product":product_j,"event":event_j, "norp":norp_j, "id":idj}

	inlist = json.dumps(tlist)
	
	#beginTime = time.time()
	#cpus = multiprocessing.cpu_count()
	#cpus = int(cpus/2) - 1
	
	#print("Using {} cpus for processing".format(cpus))
	#annotationPool = Pool(cpus)

    # storage, in case you need (this one is delated before return)
	FileToWrite = out_dir + idj + 'DALAI-API.csv'
	
	is_scanned=False
	result = []
	result.append(FileToRead)
				#ann=''
	outlist=[None]*15
	outlist[0]= ntpath.basename(FileToRead)
	outlist[4] = ''
	#return( ' What ')
	#print( FileToRead , os.path.isfile(FileToRead)) 
	if os.path.isfile(FileToRead)==True and FileToRead.lower().endswith('.pdf'):
		
		parsed_pdf = parser.from_file(FileToRead)
		#print( parsed_pdf )
		if parsed_pdf['content']==None:
			is_scanned = True
			if (is_scanned == True):
				
				textform= pdftoText(FileToRead,FileToWrite,outlist)
				ann = do_annif(FileToRead,textform,an_proj,FileToWrite,outlist,inlist,idj)
				
				
		elif parsed_pdf != None:
			print( ' DIGIBORN ')
			
			ann = do_annif(FileToRead,parsed_pdf['content'],an_proj,FileToWrite,outlist,inlist,idj)
						
				
	if os.path.isfile(FileToRead)==True and FileToRead.lower().endswith(('.png','.tiff','.jpg','jpeg','.tif')):
						#print(FileToRead)
				#outlist[1] = 'Yes'
				img = cv2.imread(FileToRead)
				text = image_to_string(img)
				tikafile = parser.from_buffer(text)
				outlist[4] = language.from_buffer(tikafile)
						#print(len(text))
				
				ann = do_annif(FileToRead,text,an_proj,FileToWrite,outlist,inlist,idj)

	if os.path.isfile(FileToRead)==True and FileToRead.lower().endswith(('.xml','.html','.txt')):
		tikafile = parser.from_file(FileToRead)
		ann = do_annif(FileToRead,tikafile['content'],an_proj,FileToWrite,outlist,inlist,idj)

	header_names = ['Tiedosto','ORG','PERSON','Annif','Kieli','Päivämäärät','y_tunnus','Diaari','Hetu','loc','gpe','product','event','norp', 'id'] 
	

	new = pd.read_csv(FileToWrite, sep=';', names= header_names, encoding='utf8')
	print(FileToWrite)
	df = pd.DataFrame(new)
	result = df.to_json(orient="split")
	parsed = json.loads(result)
	ret = json.dumps(parsed)
	#print( ' Done ')
	os.system( 'rm ' + FileToRead) 
	os.system( 'rm ' + FileToWrite)
	
	return ret

