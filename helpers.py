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


""" Finds image for the first year before the input year """
def getImage(year, base):
	images = []
	#collect all image files bigger than year
	for root, dirs, files, in os.walk("images/validYears"):
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
