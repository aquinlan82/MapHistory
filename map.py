import random
from tkinter import ttk
from PIL import Image, ImageTk
import pyodbc
import tkinter as tk
import sys
import os
from zoom import *

"""
Map History
Created by Allison Quinlan
Started May 2020

"""


rectangles = []   #all pixels drawn over map
windows = True	#windows or linux os

""" connects to SQL database """
def getServerConnection():
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


""" selects colors of database entries at a given place and time  """
def getColor(year, place):
	conn = getServerConnection()
	cursor = conn.cursor()
	string = "Select R,G,B from places.Locations Where place=\"" + place + "\" AND yearStart<"+year+" AND yearEnd>"+year
	cursor.execute(string)
	for row in cursor:
		return row

""" selects all colors of entries in database in certain time """
def getAllColors(year):
	conn = getServerConnection()
	cursor = conn.cursor()
	string = "Select R,G,B from places.Locations Where yearStart<"+year+" AND yearEnd>"+year
	cursor.execute(string)
	return cursor

""" Finds image for the first year before the input year """
def getImage(year):
	global base
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

""" Change every pixel that is the given color to red on the image for that year """
"""Better Method? """
def drawCountry(color, year):
	img = getImage(year)
	pixels = img.load()
	mapLen, mapHei = img.size
	for y in range(mapHei):
		for x in range(mapLen):
			if pixels[x,y][0] == color[0] and pixels[x,y][1] == color[1] and pixels[x,y][2] == color[2]:
				rectid = canvas.create_rectangle(x,y,x+1,y+1, fill="red",outline="red")
				#store pixels for zooming
				global rectangles
				rectangles.append(rectid)

"""Changes all pixels that are a color in the color array to red """
"""Better Method? """
def drawAllCountry(colors, year):
	listColor = []
	for color in colors:
		listColor.append(list(color))
	img = getImage(year)
	pixels = img.load()
	mapLen, mapHei = img.size
	for y in range(mapHei):
		for x in range(mapLen):
			pixel = [pixels[x,y][0],pixels[x,y][1],pixels[x,y][2]]
			if pixel in listColor:
				rectid = canvas.create_rectangle(x,y,x+1,y+1, fill="red",outline="red")
				global rectangles
				rectangles.append(rectid)

""" Checks input and draws all countries if valid """
def buttonClickAll():
	valid = resetAndClean(False)
	if valid:
		year = yearEntry.get()
		colors = getAllColors(year)
		if colors==None:
			infoLabel.config(text="Not in database")
		else:	
			infoLabel.config(text=str(year))
			drawAllCountry(colors, year)
			app.clickWheel(rectangles)

"""Pressing Enter calls a method with an argument,
but should perform same action as button click """
def wrapper(arg):
	buttonClick()


""" Checks input and draws country if valid """
def buttonClick():
	valid = resetAndClean(True)
	if valid:
		year = yearEntry.get()
		place = placeEntry.get()
		color = getColor(year, place)
		if color==None:
			infoLabel.config(text="Not in database")
		else:	
			infoLabel.config(text=place)
			drawCountry(color,year)
			app.clickWheel(rectangles)

""" Returns if data inputs are valid """
def resetAndClean(checkPlace):
	global rectangles

	#clear canvas
	for rectid in rectangles:
		canvas.delete(rectid)
	rectangles = []

	#clean input
	year = yearEntry.get()
	place = placeEntry.get()
	if year == "":
		infoLabel.config(text="Please set year")	
	elif int(year) < 0 or int(year) > 2020:
		infoLabel.config(text="Please set valid year")
	elif place == "" and checkPlace:
		infoLabel.config(text="Please set country")
	else:
		return True
	return False

""" Main Method """
curX = 40
curY = 40

winLen = 1000
winHei = 600

#window settings
interpretor = sys.executable
if interpretor == "/usr/bin/python3":
	windows = False
root = tk.Tk()
root.title("Map History")
root.geometry(str(winLen)+"x"+str(winHei))

#picture settings  
global base
base = os.getcwd()
if windows:
	base = base + "\\images\\validYears\\"
else:
	base = base + "/images/validYears/"
img = base + "map.png"
app = Zoom_Advanced(root, path=img)
canvas = app.canvas   #canvas added at 0,0 with colSpan of 2

#control panel
root.columnconfigure(0,weight=1,minsize=300)
root.columnconfigure(1,weight=2)

tk.Label(root, text="Year").grid(row=1,column=0,sticky=tk.E, padx=10)
yearEntry = tk.Entry(root)
yearEntry.insert(0,"2015")
yearEntry.grid(row=1, column=1, sticky=tk.W)
yearEntry.bind("<Return>", wrapper)

tk.Label(root, text="Place").grid(row=2,column=0, sticky=tk.E, padx=10)
placeEntry = tk.Entry(root)
placeEntry.insert(0,"US")
placeEntry.grid(row=2, column=1, sticky=tk.W)
placeEntry.bind("<Return>", wrapper)

singleCountryBtn = tk.Button(root, text="Find Country", command=buttonClick, width=10, height=3)
singleCountryBtn.grid(row=3, column=0, sticky=tk.E) 

allCountryBtn = tk.Button(root, text="Find all in year", command=buttonClickAll, width=10, height=3)
allCountryBtn.grid(row=3, column=1, sticky=tk.W)

infoLabel = tk.Label(root, text="")
infoLabel.grid(row=4,column=0,columnspan=2)


#Loop
root.mainloop()


