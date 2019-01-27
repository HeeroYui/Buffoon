#!/usr/bin/python
# -*- coding: utf-8 -*-
##
## @author Edouard DUPIN
##
## @copyright 2012, Edouard DUPIN, all right reserved
##
## @license MPL v2.0 (see license file)
##

import os
import shutil
import errno
import fnmatch
import stat


def create_directory(path):
	try:
		os.stat(path)
	except:
		os.makedirs(path)

def create_directory_of_file(file):
	path = os.path.dirname(file)
	create_directory(path)

def file_write_data(path, data):
	print("    write file: " + path)
	create_directory_of_file(path)
	file = open(path, "w")
	file.write(data)
	file.close()
	return True

def remove_file(path):
	if os.path.isfile(path):
		os.remove(path)
	elif os.path.islink(path):
		os.remove(path)

def file_read_data(path, binary=False):
	print("path= " + path)
	if not os.path.isfile(path):
		return ""
	if binary == True:
		file = open(path, "rb")
	else:
		file = open(path, "r")
	data_file = file.read()
	file.close()
	return data_file

def copy_file(src, dst):
	print("copy " + src + " ==> " + dst)
	create_directory_of_file(dst)
	shutil.copyfile(src, dst)

def copy_anything(src, dst):
	print(" copy anything : '" + str(src) + "'")
	print("            to : '" + str(dst) + "'")
	if os.path.isdir(os.path.realpath(src)):
		tmp_path = os.path.realpath(src)
		tmp_rule = ""
	else:
		tmp_path = os.path.dirname(os.path.realpath(src))
		tmp_rule = os.path.basename(src)
	
	for root, dirnames, filenames in os.walk(tmp_path):
		deltaRoot = root[len(tmp_path):]
		while     len(deltaRoot) > 0 \
		      and (    deltaRoot[0] == '/' \
		            or deltaRoot[0] == '\\' ):
			deltaRoot = deltaRoot[1:]
		if deltaRoot != "":
			return
		tmpList = filenames
		if len(tmp_rule) > 0:
			tmpList = fnmatch.filter(filenames, tmp_rule)
		# Import the module :
		for cycleFile in tmpList:
			#for cycleFile in filenames:
			copy_file(os.path.join(tmp_path, deltaRoot, cycleFile),
			          os.path.join(dst, deltaRoot, cycleFile))


##
## @brief Get list of all Files in a specific path (with a regex)
## @param[in] path (string) Full path of the machine to search files (start with / or x:)
## @param[in] regex (string) Regular expression to search data
## @param[in] recursive (bool) List file with recursive search
## @param[in] remove_path (string) Data to remove in the path
## @return (list) return files requested
##
def get_list_of_file_in_path(path, filter, recursive = False, remove_path=""):
	out = []
	if os.path.isdir(os.path.realpath(path)):
		tmp_path = os.path.realpath(path)
	else:
		print("[E] path does not exist : '" + str(path) + "'")
	
	for root, dirnames, filenames in os.walk(tmp_path):
		deltaRoot = root[len(tmp_path):]
		while     len(deltaRoot) > 0 \
		      and (    deltaRoot[0] == '/' \
		            or deltaRoot[0] == '\\' ):
			deltaRoot = deltaRoot[1:]
		if     recursive == False \
		   and deltaRoot != "":
			return out
		tmpList = []
		for elem in filter:
			tmpppp = fnmatch.filter(filenames, elem)
			for elemmm in tmpppp:
				tmpList.append(elemmm)
		# Import the module :
		for cycleFile in tmpList:
			#for cycleFile in filenames:
			add_file = os.path.join(tmp_path, deltaRoot, cycleFile)
			if len(remove_path) != 0:
				if add_file[:len(remove_path)] != remove_path:
					print("[E] Request remove start of a path that is not the same: '" + add_file[:len(remove_path)] + "' demand remove of '" + str(remove_path) + "'")
				else:
					add_file = add_file[len(remove_path)+1:]
			out.append(add_file)
	return out;
