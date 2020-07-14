import random
from tkinter import ttk
from PIL import Image, ImageTk
import pyodbc
import tkinter as tk
import sys
import os
from zoom import *

""" connects to SQL database """
def getServerConnection(windows):
	driver = "{MySQL ODBC 8.0 Driver}"
	server = "127.0.0.1"
	database = "places"
	username = "root"
	password = "Password!"
	if windows:
		conn = pyodbc.connect("DSN=dsn;UID=root;PWD=Password!")
	else:
		conn = pyodbc.connect("Driver="+driver+";SERVER="+server+";DATABASE="+database+";USER="+username+";PASSWORD="+password+";")
	return conn

""" Determines how to get to images """
def getImagePath(windows, small):
	path = "images/"
	if windows:
		path = path + "/"
	if small:
		path = path + "smallV"
	else:
		path = path + "v"
	path = path + "alidYears/"
	if windows:
		path = path + "/"
	return path

"""Determines image for first year before input year """
def getAnyImage(year, base, small):
	images = []
	#collect all image files bigger than year
	for root, dirs, files, in os.walk(getImagePath(False, small)):
		for file in files:
			if file.endswith(".png"):
				path = file.split(".")[0]
				try:
					if int(path) <= year:
						images.append(int(path))	
				except:
					pass
	images.sort()

	#select file
	filename = base + "2020.png"
	if len(images) > 0:
		filename = base + str(images[-1]) + ".png"
	img = Image.open(filename)
	return img

""" Finds big image for the first year before the input year """
def getImage(year, base):
	return getAnyImage(year, base, False)

""" Finds small image for the first year before the input year """
def getSmallImage(year, base):
	return getAnyImage(year, base, True)
