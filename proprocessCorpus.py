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
import scipy.io.wavfile as wavfile

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
		sample_rate, audio_data = wavfile.read(filename)
	else:
		debug.error("Not supported file type: '" + str(filename[-3:]) + "' suported: [wav]")
	debug.info("Read: " + str(len(audio_data)) + " sample(s)")
	
	audio_16k = resampy.resample(audio_data, 48000, 16000)
	
	debug.info("write: " + str(len(audio_16k)) + " sample(s)")
	
	filename_out = os.path.join(args.output, input_data["audio_filename"])
	wavfile.write(filename_out, 16000, audio_16k)
	input_data["audio_sample_rate"] = 16000
	filename_out_json = os.path.join(args.output, os.path.basename(elem))
	with open(filename_out_json, 'w') as outfile:
		json.dump(input_data, outfile, indent="\t")


debug.info("Finish")

