
import io, os, urllib, requests, re, webbrowser, json, glob, time

# Imports the Google Cloud client library
from google.cloud import vision
from google.cloud.vision import types

from subprocess import call

# import Bsoup
from bs4 import BeautifulSoup

from PIL import Image

def crop(image_path, coords, saved_location):

    image_obj = Image.open(image_path)
    cropped_image = image_obj.crop(coords)
    cropped_image.save(saved_location)
    #cropped_image.show()


def run_ocr(img_name):

	print "running OCR..."
	client = vision.ImageAnnotatorClient()

	file_name = os.path.join(os.path.dirname(__file__),'Cropped.jpg')

	with io.open(file_name, 'rb') as image_file:
	    content = image_file.read()

	image = types.Image(content=content)

	response = client.text_detection(image=image)
	texts = response.text_annotations

	all_text = texts[0].description.strip()

	lines = all_text.split("\n")

	ans_1 = lines[-3].lower().encode('utf-8')
	ans_2 = lines[-2].lower().encode('utf-8')
	ans_3 = lines[-1].lower().encode('utf-8')

	del lines[-1]
	del lines[-1]
	del lines[-1]

	question = u" ".join([line.strip() for line in lines]).encode('utf-8')

	reverse = True
        
	return { 
		"question": question,
		"ans_1": ans_1,
		"ans_2": ans_2,
		"ans_3": ans_3,
	}

def google(q_list, num):

	params = {"q":" ".join(q_list), "num":num}
	url_params = urllib.urlencode(params)
	google_url = "https://www.google.com/search?" + url_params
	r = requests.get(google_url)

	soup = BeautifulSoup(r.text,"html.parser")
	spans = soup.find_all('span', {'class' : 'st'})

	text = u" ".join([span.get_text() for span in spans]).lower().encode('utf-8').strip()

	return text

def rank_answers(question_block):

	print "rankings answers..."
	
	question = question_block["question"]
	ans_1 = question_block["ans_1"]
	ans_2 = question_block["ans_2"]
	ans_3 = question_block["ans_3"]

	reverse = True

	if " not " in question.lower():
		print "reversing results..."
		reverse = False

	text = google([question], 75)

	results = []

	results.append({"ans": ans_1, "count": text.count(ans_1)})
	results.append({"ans": ans_2, "count": text.count(ans_2)})
	results.append({"ans": ans_3, "count": text.count(ans_3)})

	sorted_results = []

	sorted_results.append({"ans": ans_1, "count": text.count(ans_1)})
	sorted_results.append({"ans": ans_2, "count": text.count(ans_2)})
	sorted_results.append({"ans": ans_3, "count": text.count(ans_3)})

	sorted_results.sort(key=lambda x: x["count"], reverse=reverse)


	if (sorted_results[0]["count"] == sorted_results[1]["count"]):

		print "running tiebreaker..."

		text = google([question, ans_1, ans_2, ans_3], 150)

		results = []

		results.append({"ans": ans_1, "count": text.count(ans_1)})
		results.append({"ans": ans_2, "count": text.count(ans_2)})
		results.append({"ans": ans_3, "count": text.count(ans_3)})

	return results

def print_question_block(question_block):

	print "\n"
	print "Q: ", question_block["question"]
	print "1: ", question_block["ans_1"]
	print "2: ", question_block["ans_2"]
	print "3: ", question_block["ans_3"]
	print "\n"

def save_question_block(question_block):

	question = question_block["question"].replace(",", "").replace("\"", "").replace("\'", "")
	ans_1 = question_block["ans_1"].replace(",", "").replace("\"", "").replace("\'", "")
	ans_2 = question_block["ans_2"].replace(",", "").replace("\"", "").replace("\'", "")
	ans_3 = question_block["ans_3"].replace(",", "").replace("\"", "").replace("\'", "")

	with open('questions.csv', 'a') as file:
		file.write("\t".join([question,ans_1,ans_2,ans_3 + "\n"]))
		file.close()
		
def print_results(results):

	print "\n"

	small = min(results, key= lambda x: x["count"])
	large = max(results, key= lambda x: x["count"])

	for (i,r) in enumerate(results):
		text = "%s - %s" % (r["ans"], r["count"])

		

		if r["ans"] == large["ans"]:
			print text
		elif r["ans"] == small["ans"]:
			print text
		else:
			print text

	print "\n"

while True:

    Continue = False
    
    for filename in glob.glob("A0001*"):
        if (os.path.isfile(filename)) == True:
            Continue = True
        else:
            Continue = False
            
    if Continue == True:

        time.sleep(0.1)
        
        for filename in glob.glob("Original.jpg"):
            os.remove(filename) 
        for filename in glob.glob("A0001*"):
            os.rename(filename,"Original.jpg")

        image = 'Original.jpg'
        crop(image, (50, 200, 500, 620), 'Cropped.jpg')
        print("Cropped?")

        qlist = run_ocr('Cropped.jpg')
        google(qlist,50)
        results = rank_answers(qlist)
        print_question_block(qlist)
        save_question_block(qlist)
        print_results(results)

