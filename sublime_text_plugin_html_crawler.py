#!/usr/bin/python
# -*- coding: utf-8 -*-

# parse the naoqi documentation and creates a text file suitable for creating a Sublime Text plugin
# Mike McFarlane
# v0-1: 23 Aug 2013, crawl docs and build a list of methods, classes and frameworks
# TODO: BeautifulSoup - done
# TODO: check for deprecated APIs, fully re-factor using Beautiful Soup and the full html for each api doc
# TODO: rather than create method_dictionary, use dictionary comprehension

"""look for <dl class="function"> for the start of each method """
""" then get everything between <dt and </dt> """
"""look for first instance of <a class="reference internal" href="../stdtypes.html# then title=" for return type """
"""look for <tt class="descclassname"> for class """
"""look for <tt class="descname"> for methods """
"""look for second instance of <a class="reference internal" for arguments """

import fnmatch
import os
from bs4 import BeautifulSoup

def get_html_file_list():
	"""finds all the HTML API docs in a defined folder"""
	"""returns the list of html files as a list and writes them to a file"""

	PATH = '/Users/mikemcfarlane/Desktop/NAO_doc/doc-release-1.14-public/naoqi'
	pattern = '*api*.html'

	f = open("html_list.txt", "w")
	html_list = []
	 
	for root, dirs, files in os.walk(PATH):
	    for filename in fnmatch.filter(files, pattern):
	        #print (os.path.join(root, filename))
	        f.write((os.path.join(root, filename)) + "\n")
	        html_list.append((os.path.join(root, filename)))
	f.close()
	return html_list

def find_methods(html_list):
	"""crawl all the html api docs and create a list with all the methods in"""
	"""returns the methods list still in html tagged form"""

	file_dump = open("file_dump.txt", "w")

	methods_html = []
	for api_file in html_list:
		try:
			f = open(api_file, "r")			
		except:
			print "Error finding: " + api_file
			return None
		file_contents = f.read()
		index = 0
		while True:
			start_method = file_contents.find("""<dl class="function">""", index)
			if start_method == -1:
				break
			else:
				start_dt_tag = file_contents.find("<dt", start_method)
				end_dt_tag = file_contents.find("</dt>", start_dt_tag)
				method_info = file_contents[start_dt_tag + 4:end_dt_tag]
				methods_html.append("--" + api_file + "--" + method_info)
				index = end_dt_tag
				#file_dump.write(api_file +  "\n")
				file_dump.write("--" + api_file + "--" + method_info + "\n\n")				
		f.close()
	file_dump.close()
	return methods_html

def find_arguments(arg_string):
	#find the arguments and tidy them up
	#returns a list of the arguments
	start_string = arg_string.find("(") + 1
	end_string = arg_string.find(")")
	arg_string = arg_string[start_string:end_string]
	#remove ampersand chars
	arg_string = arg_string.replace("&", "")
	arg_list = []
	while True:
		comma_position = arg_string.find(",", 0)
		if comma_position == -1:
			arg_list.append(str(arg_string))
			break
		else:
			arg_list.append(str(arg_string[:comma_position]))
			arg_string = arg_string[comma_position+2:]
	return arg_list

def build_methods_dictionary(methods_html):
	"""build a dictionary of relevant info for each method"""
	"""return a dictionary"""
	#dictionary which will contain all info for all the methods and classes
	methods_dictionary = {}
	#dictionary which contains individual info for each method
	method_dictionary = {}
	
	for i in methods_html:		
		#find framework name
		start_framework = i.find("/naoqi/", 0) + len('/naoqi/')
		end_framework = i.find("/", start_framework)
		framework = i[start_framework:end_framework].upper()
		#find return type, class, method and arguments
		#need to remove the space in 'reference internal' or not recognised as class by beautiful soup
		j = i.replace("reference internal", "referenceinternal")
		soup = BeautifulSoup(j)
		first_internal_index = 0
		for i in soup.select(".referenceinternal"):
			if first_internal_index == 0:
				nao_return = i.string
				first_internal_index = 1
			nao_arg_list = find_arguments(soup.get_text())
		for i in soup.select(".descclassname"):
			#slice the :: off the end of the string
			nao_class = i.string[:-2]
		for i in soup.select(".descname"):
			nao_method = i.string
		#print it all out
		# print "Framework: " + framework
		# print "Class: " + nao_class
		# print "Method: " + nao_method
		# for i in nao_arg_list:
		# 	print "Argument: " + i
		# print "Returns: " + nao_return
		# print "\n"
		#save to method_dictionary, declaring a new empty one each time
		method_dictionary = {}
		key = nao_class + "::" + nao_method
		method_dictionary['framework'] = framework
		method_dictionary['class'] = nao_class
		method_dictionary['method'] = nao_method
		arg_index = 0
		for k in nao_arg_list:
			arg_number = "arg" + str(arg_index)
			method_dictionary[arg_number] = k
			arg_index += 1			
		method_dictionary['return'] = nao_return
		#save the dictionary into the main dictionary
		methods_dictionary[key] = method_dictionary
	return methods_dictionary

def write_methods_to_file(methods_dictionary):
	#write the sublime text autocompletions file
	#format, see /Users/mikemcfarlane/Dropbox/Code/robotc-sublime-text-plugin/RobotC_v0-2/RobotC.sublime-completions
	#and /Users/mikemcfarlane/Library/Application Support/Sublime Text 2/Packages/Python
	
	#just writing some stuff out to a file to test operation:-)
	# naoqi_sublime_completions = open("naoqi.sublime-completions", "w")
	# for i in methods_dictionary:
	# 	naoqi_sublime_completions.write("key: " + i + "\n")
	# 	for j in methods_dictionary[i]:
	# 		naoqi_sublime_completions.write(j + " " + methods_dictionary[i][j] + "\n")
	# naoqi_sublime_completions.close()

	#write a proper autocompletions trigger file
	naoqi_sublime_completions = open("naoqi.sublime-completions", "w")
	naoqi_sublime_completions.write("{" + "\n")
	naoqi_sublime_completions.write('''\t"scope": "source.py"''' + "\n")
	naoqi_sublime_completions.write('''\t"completions":''' + "\n")
	naoqi_sublime_completions.write('''\t[''' + "\n")
	# for i in methods_dictionary:
	# 	naoqi_sublime_completions.write("key: " + i + "\n")
	# 	for j in methods_dictionary[i]:
	# 		naoqi_sublime_completions.write(j + " " + methods_dictionary[i][j] + "\n")
	pre_text = '\t\t{"trigger:"\t"'
	mid_text = '","contents": "'
	end_text = '"},\n'
	for i in methods_dictionary:
		#assemble the trigger part of the string
		nao_method = methods_dictionary[i]['method']
		nao_class = methods_dictionary[i]['class']
		nao_framework = methods_dictionary[i]['framework']
		nao_trigger = nao_method + "\t" + nao_class + "\t" + nao_framework
		#assemble the contents part of the string
		nao_content = methods_dictionary[i]['method'] + "()"
		#assemble the argument string
		
		#and write to file
		naoqi_sublime_completions.write(pre_text + nao_trigger + mid_text + nao_content + end_text)

	naoqi_sublime_completions.write('''\t]''' + "\n")
	naoqi_sublime_completions.write("}" + "\n")
	naoqi_sublime_completions.close()

		
html_list = get_html_file_list()
methods_html = find_methods(html_list)
methods_dictionary = build_methods_dictionary(methods_html)
# for i in methods_dictionary:
# 	print "key: " + i
# 	for j in methods_dictionary[i]:
# 		print j + " " + methods_dictionary[i][j]
# 	print "\n"
write_methods_to_file(methods_dictionary)



