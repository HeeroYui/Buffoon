#!/usr/bin/python
# -*- coding: utf-8 -*-
##
## @author Edouard DUPIN
##
## @license MPL v2.0 (see license file)
##

import os
import tools
import debug
import argparse
import math
import json
import resampy
import numpy as np
import scipy.io.wavfile
import scipy.signal



parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", help="Input directory",
                                     default="")
parser.add_argument("-o", "--output", help="Output directory",
                                      default="out")
parser.add_argument("-v", "--verbose", help="display all LOGS",
                                       default=False,
                                       action='store_true')
args = parser.parse_args()

debug.info("***********************************")

# ---------------------------------------------
# -- check input
# ---------------------------------------------
if args.verbose == True:
	debug.set_level(6);
if    args.input == None \
   or args.input == "" :
	debug.error("must set an input directory")

tools.create_directory(args.output)

debug.info("==================================================================================================")
debug.info("== Preprocess corpus data: " + args.input + " to " + args.output)
debug.info("==================================================================================================")

debug.info("Get list of corpus files:")
audio_corpus_element = tools.get_list_of_file_in_path(args.input, ["*.json"], recursive=True)

debug.info("Corpus count " + str(len(audio_corpus_element)) + " element(s)")
elem_id = 0
for elem in audio_corpus_element:
	debug.info("---------------------------[ " + str(elem_id) + " / " + str(len(audio_corpus_element)) + " ]---------------------------------------")
	elem_id += 1
	debug.info("Element: " + elem)
	with open(elem) as file:
		input_data = json.load(file)
	"""{
		"user": "Edouard DUPIN",
		"value": "bonjour",
		"language": "FR_fr",
		"time": 3088499332851,
		"audio_format": "int16",
		"audio_channel": 1,
		"audio_sample_rate": 48000,
		"audio_filename": "FR_fr_Edouard DUPIN_3088499332851.raw"
	}
	"""
	if "audio_format" not in input_data.keys():
		debug.error(" ==> missing field 'audio_format' ...")
	if input_data["audio_format"] != "int16":
		debug.error(" ==> field 'audio_format' have wrong value: '" + str(input_data["audio_format"]) + "' suported: [int16]")
	if "audio_channel" not in input_data.keys():
		debug.error(" ==> missing field 'audio_channel' ...")
	if input_data["audio_channel"] != 1:
		debug.error(" ==> field 'audio_channel' have wrong value: '" + str(input_data["audio_channel"]) + "' suported: [1]")
	if "audio_sample_rate" not in input_data.keys():
		debug.error(" ==> missing field 'audio_sample_rate' ...")
	if input_data["audio_sample_rate"] != 48000:
		debug.error(" ==> field 'audio_sample_rate' have wrong value: '" + str(input_data["audio_sample_rate"]) + "' suported: [48000]")
	if "audio_filename" not in input_data.keys():
		debug.error(" ==> missing field 'audio_filename' ...")
	filename = os.path.join(os.path.dirname(elem), input_data["audio_filename"])
	if filename[-3:] == "wav":
		sample_rate, audio_data = scipy.io.wavfile.read(filename)
	else:
		debug.error("Not supported file type: '" + str(filename[-3:]) + "' suported: [wav]")
	debug.info("Read: " + str(len(audio_data)) + " sample(s)")
	
	
	#######################################################
	## Step 1: Generate speech areas (work on input, because I am sure that the data is not modified
	#######################################################
	audio_data_absolute = np.absolute(audio_data)
	shape = np.copy(audio_data_absolute)
	# average of the anbiant noise
	avg = 0
	# count represent the number of basic sample to etalonate the generic ambiant noise
	count = 0
	count_all = 0
	set_value = 32767
	# number of sampel of the anbiant noise calculation
	ambiant_basic_size = 48000/4 # : 1/4 s ==> the cormus is manage to have 1 second before starting to have real data voice
	for sample_audio in audio_data_absolute:
		#shape[count_all] = 0
		count_all += 1
		if count < ambiant_basic_size:
			# Remove the 0 padding
			if count == 0 and sample_audio == 0:
				continue
			elif count == 0:
				debug.info("start data " + str(count_all) + " samples (at value 0)")
			count += 1
			avg += sample_audio
		elif count == ambiant_basic_size:
			count += 1
			avg /= ambiant_basic_size
			debug.info("basic ambiant is: " + str(avg) + " start annalyse at : " + str(count_all/48000) + " sec")
			if avg <= 327.67:
				avg = int(327.67)
			else:
				avg = int(avg * 1.1)
			## set_value = avg
			debug.info("    inspect at " + str(avg))
		else:
			if sample_audio >= avg:
				shape[count_all-1] = set_value;
	
	#filename_out = os.path.join(args.output, input_data["audio_filename"] + "_ori.wav")
	#scipy.io.wavfile.write(filename_out, 48000, audio_data)
	#filename_out = os.path.join(args.output, input_data["audio_filename"] + "_abs.wav")
	#scipy.io.wavfile.write(filename_out, 48000, audio_data_absolute)
	#filename_out = os.path.join(args.output, input_data["audio_filename"] + "_shape1.wav")
	#scipy.io.wavfile.write(filename_out, 48000, shape)
	
	windows = int(48000 * 0.02)
	count_all = 0
	count = 0
	for sample_audio in shape:
		count_all += 1
		if sample_audio == set_value:
			count = windows
			continue
		count -= 1
		if count >= 0:
			shape[count_all-1] = set_value;
	shape = np.flip(shape)
	count_all = 0
	count = 0
	for sample_audio in shape:
		count_all += 1
		if sample_audio == set_value:
			count = windows
			continue
		count -= 1
		if count >= 0:
			shape[count_all-1] = set_value;
		else:
			shape[count_all-1] = 0
	shape = np.flip(shape)
	
	filename_out = os.path.join(args.output, input_data["audio_filename"] + "_shape.wav")
	scipy.io.wavfile.write(filename_out, 48000, shape)
	
	count_all = 0
	table_voice_detected = [[0,False]]
	previous = False
	# use numpy slicing: [start:stop:step] https://docs.scipy.org/doc/numpy/reference/arrays.indexing.html#basic-slicing-and-indexing
	for sample_audio in shape[3:len(shape):3]:
		count_all += 1
		if previous == False:
			if sample_audio == set_value:
				table_voice_detected.append([count_all, True])
				previous = True
		else:
			if sample_audio == 0:
				table_voice_detected.append([count_all, False])
				previous = False
	
	#######################################################
	## Step 2: Resample
	#######################################################
	audio_16k = resampy.resample(audio_data, 48000, 16000, filter='kaiser_best')
	#audio_16k = resampy.resample(audio_data, 48000, 16000, filter='kaiser_fast')
	
	debug.info("write: " + str(len(audio_16k)) + " sample(s)")
	
	filename_out = os.path.join(args.output, input_data["audio_filename"])
	scipy.io.wavfile.write(filename_out, 16000, audio_16k)
	# create new data format:
	output_data = {
		"value": input_data["value"],
		"language": input_data["language"],
		"audio_sample_rate": 16000,
		"audio_filename": input_data["audio_filename"],
		"VAD": table_voice_detected,
		"action": [
			{
				"type": "resampling",
				"tool": "resampy",
				"desc": "48000 ==> 16000",
				"src": elem,
			},{
				"type": "auto VAD",
				"tool": "internal_1",
				"desc": "When control the input data, with small noise, we can detect voice, just with signal power ...",
				"src": elem,
			},
		],
	}
	
	
	filename_out_json = os.path.join(args.output, os.path.basename(elem))
	with open(filename_out_json, 'w') as outfile:
		json.dump(output_data, outfile, indent="\t")


debug.info("Finish")

