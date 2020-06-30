import random
from tkinter import ttk
from PIL import Image, ImageTk
import pyodbc
import tkinter as tk
import sys
import os


class Zoom_Advanced(ttk.Frame):

	"""Initialize all needed variables"""
	def __init__(self, mainframe, path):
		ttk.Frame.__init__(self, master=mainframe)
		self.master.title("Map History")
		self.canvas = tk.Canvas(self.master, highlightthickness=0,
								xscrollcommand=self.scrollX, yscrollcommand=self.scrollY)
		self.canvas.grid(row=0, column=0, sticky='nswe', columnspan=2, padx = 30, pady=20)
		self.canvas.update() 
		self.zooms = []
		self.master.rowconfigure(0, weight=1)
		self.master.columnconfigure(0, weight=1)
		self.canvas.bind('<Configure>', self.show_image) 
		self.canvas.bind('<MouseWheel>', self.wheel)  # with Windows and MacOS, but not Linux
		self.canvas.bind('<Button-5>',   self.wheel)  # only with Linux, wheel scroll down
		self.canvas.bind('<Button-4>',   self.wheel)  # only with Linux, wheel scroll up

		self.image = Image.open(path)  
		self.width, self.height = self.image.size
		self.imscale = 1.0 
		self.delta = 1.3 
		self.container = self.canvas.create_rectangle(0, 0, self.width, self.height, width=0)
		self.show_image()

	"""Not yet implemented"""
	def scrollX(arg1, arg2,arg3):
		pass
		#self.canvas.xview(*args, **kwargs)  # scroll horizontally
		#self.show_image()  # redraw the image

	"""Not yet implemented"""
	def scrollY(arg1, arg2,arg3):
		pass
		#self.canvas.yview(*args, **kwargs)  # scroll vertically
		#self.show_image()  # redraw the image

	"""Zooms in if image is more than 30 pixels and returns new scale"""
	def zoomIn(self):
		i = min(self.width, self.height)
		if int(i * self.imscale) < 30:
			return 1.0
		else: 
			self.imscale /= self.delta
			return 1.0 / self.delta

	"""Zooms out if pixels smaller than images and returns new scale"""
	def zoomOut(self):
		i = min(self.canvas.winfo_width(), self.canvas.winfo_height())
		if i < self.imscale:
			return 1.0
		else:
			self.imscale *= self.delta
			return self.delta

	"""Zooms when mouse wheel spun"""
	def wheel(self, event):
		self.zooms.append([event,self.imscale,self.delta])

		#only zoom in image area
		x = self.canvas.canvasx(event.x)
		y = self.canvas.canvasy(event.y)
		bbox = self.canvas.bbox(self.container)
		if bbox[0] < x < bbox[2] and bbox[1] < y < bbox[3]: pass
		else: return 

		# Respond to Linux (event.num) or Windows (event.delta) wheel event
		scale = 1.0
		if event.num == 5 or event.delta == -120: 
			scale = self.zoomIn()
		if event.num == 4 or event.delta == 120:  # scroll up
			scale = self.zoomOut()

		self.canvas.scale('all', x, y, scale, scale)  # rescale all canvas objects
		self.show_image()

	"""Zooms all red pixels"""
	def clickWheel(self, rectangles):
		for data in self.zooms:
			even = data[0]
			imscale = data[1]
			delta = data[2]
			x = self.canvas.canvasx(even.x)
			y = self.canvas.canvasy(even.y)
			bbox = self.canvas.bbox(self.container)  
			if bbox[0] < x < bbox[2] and bbox[1] < y < bbox[3]: pass  
			else: return 
			scale = 1.0
			# Respond to Linux (event.num) or Windows (event.delta) wheel event
			if even.num == 5 or even.delta == -120:  # scroll down
				i = min(self.width, self.height)
				if int(i * imscale) < 30: return  # image is less than 30 pixels
				imscale /= delta
				scale   /= delta
			if even.num == 4 or even.delta == 120:  # scroll up
				i = min(self.canvas.winfo_width(), self.canvas.winfo_height())
				if i < imscale: return  # 1 pixel is bigger than the visible area
				imscale *= delta
				scale   *= delta
			for rect in rectangles:
				self.canvas.scale(rect, x, y, scale, scale)  # rescale all canvas objects
		self.show_image()

	"""Show image on canvas"""
	def show_image(self, event=None):
		# get image area and remove 1 pixel shift at the sides of the bbox1
		bbox1 = self.canvas.bbox(self.container)
		bbox1 = (bbox1[0] + 1, bbox1[1] + 1, bbox1[2] - 1, bbox1[3] - 1)

		#get canvas coords
		bbox2 = (self.canvas.canvasx(0),
				 self.canvas.canvasy(0),
				 self.canvas.canvasx(self.canvas.winfo_width()),
				 self.canvas.canvasy(self.canvas.winfo_height()))

		#get coords of image tile
		x1 = max(bbox2[0] - bbox1[0], 0) 
		y1 = max(bbox2[1] - bbox1[1], 0)
		x2 = min(bbox2[2], bbox1[2]) - bbox1[0]
		y2 = min(bbox2[3], bbox1[3]) - bbox1[1]
		
		if int(x2 - x1) > 0 and int(y2 - y1) > 0:  # show image if it in the visible area
			x = min(int(x2 / self.imscale), self.width)   
			y = min(int(y2 / self.imscale), self.height) 

			image = self.image.crop((int(x1 / self.imscale), int(y1 / self.imscale), x, y))
			imagetk = ImageTk.PhotoImage(image.resize((int(x2 - x1), int(y2 - y1))))
			imageid = self.canvas.create_image(max(bbox2[0], bbox1[0]), max(bbox2[1], bbox1[1]),
											   anchor='nw', image=imagetk)
			#self.canvas.coords(imageid,20,20)


			self.canvas.lower(imageid)  # set image into background
			self.canvas.imagetk = imagetk  # keep an extra reference to prevent garbage-collection
