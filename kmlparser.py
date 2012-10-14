import xml.etree.ElementTree as ET
import zipfile
import re, uuid, os, urllib, tempfile, shutil

class KMLParserManager():
	"""Manages the discovery and parsing of ElementTrees"""
	
	def __init__(self):
		self.parsers = []
		self.pending_links = []
		self.explored_links = []
		self.placemarks = []
	
	def add_parser(self, parser):
		for link in parser.network_links():
			self.pending_links.append(link)
		self.parsers.append(parser)
	
	def explore_all(self):
		while len(self.pending_links) > 0:
			new_link = self.pending_links.pop(0)
			new_parser = KMLParser(url=new_link)
			self.add_parser(new_parser)
			self.explored_links.append(new_link)
		
		print "Total parsers created: " + repr(len(self.parsers))
	
	def all_placemarks(self):
		all_marks = []
		for p in self.parsers:
			for m in p.placemarks():
				all_marks.append(m)
		print "Total placemarks: " + repr(len(all_marks))
		self.placemarks = all_marks
		return all_marks
	

class KMLParser():
	"""Wrapper class for KML documents"""
	pass
	
	def __init__(self, **args):
		"""Constructor method"""
		
		self.tree = None
		self.namespace = None
		# self.placemarks = []
		
		# Can't create with both a file and URL
		if "filename" in args and "url" in args:
			raise ValueError
		
		# Need at least a filename or URL
		if "filename" not in args and "url" not in args:
			raise ValueError
		
		kml_file = None
		kml_filename = None
		
		if "filename" in args:
			kml_file = open(args["filename"])
			self.tree = self.parse_kml_file(kml_file)
			file.close(kml_file)
		elif "url" in args:
			try:
				kml_filename = self.fetch_remote_file(args["url"])
				kml_file = open(kml_filename)
				self.tree = self.parse_kml_file(kml_file)
				file.close(kml_file)
				shutil.rmtree(os.path.dirname(kml_filename))
			except:
				raise
		
		root_tag = self.tree.getroot().tag
		match = re.search("^{.*}", root_tag)
		
		if match.groups > 0:
			self.namespace = match.group(0)
	
	
	def parse_kml_file(self, kml_file):
		tree = ET.parse(kml_file)
		return tree
	
	def fetch_remote_file(self, url):
		is_kmz = False
		
		# Create a temporary directory for file manipulation
		temp_dir = tempfile.mkdtemp()
		filename = self.parse_filename_from_url(url)
		print "Downloading " + filename + "...",
		
		# Determine if this is a .kml or .kmz file
		if re.search("^.*\.kmz$", url):
			return self.fetch_remote_kmz(url, temp_dir, filename)
		else:
			return self.fetch_remote_kml(url, temp_dir, filename)
	
	def fetch_remote_kmz(self, url, temp_dir, filename):
		# Download file		
		try:
			urllib.urlretrieve(url, os.path.join(temp_dir, filename))
			print "done."
			
			# Extract doc.kml
			kmz = zipfile.ZipFile(os.path.join(temp_dir, filename), mode="r")
			if "doc.kml" in kmz.namelist():
				kmz.extract("doc.kml", path=temp_dir)
				print "Extracted doc.kml from " + filename
			else:
				print "Could not find doc.kml in " + filename
				
			return os.path.join(temp_dir, "doc.kml")
		except:
			print "failed."
			shutil.rmtree(temp_dir)
			raise
	
	def fetch_remote_kml(self, url, temp_dir, filename):
		try:
			urllib.urlretrieve(url, os.path.join(temp_dir, filename))
			print "done."
			return os.path.join(temp_dir, filename)
		except:
			print "failed."
			shutil.rmtree(temp_dir)
			raise
	
	def network_links(self):
		"""Finds NetworkLink elements in DOM and appends to network_links."""
		links = []
		network_links = self.tree.findall(".//%sNetworkLink" % self.namespace)
		for network_link in network_links:
			links.append(self.extract_network_link_url(network_link))
		return links
	
	def extract_network_link_url(self, network_link):
		"""Extracts the URL from a NetworkLink"""
		
		# Get Link subelement from NetworkElement
		link = network_link.findall(".//%sLink/%shref" % 
				(self.namespace, self.namespace))
		
		# Check for deprecated URL subelement if there wasn't a Link 
		# subelement
		if link == []:
			link = network_link.findall(".//%sUrl/%shref" % 
				(self.namespace, self.namespace))
		
		return link[0].text
	
	def placemarks(self):
		all_marks = []
		marks = self.tree.findall(".//%sPlacemark" % self.namespace)
		for mark in marks:
			all_marks.append(KMLPlacemark(element=mark))
		return all_marks
	
	@classmethod
	def parse_filename_from_url(self, url):
		"""Extracts and returns the filename from a URL.
	
		Returns None if no filename was found.
		"""
	
		# Check that there is a filename
		if re.search("^.*/$", url):
			return None
	
		# Extract and return filename
		match = re.search("^.*/(.*)$", url)
		if match == None:
			return None
		else:
			return match.group(1)

class KMLPlacemark():
	
	def __init__(self, **args):
		self.latitude = 0.0
		self.longitude = 0.0
		self.description = None
		
		if "element" in args:
			elem = args["element"]
			coord = elem.find(
				".//{http://www.opengis.net/kml/2.2}coordinates")
			desc = elem.find(".//{http://www.opengis.net/kml/2.2}description")
			
			self.latitude, self.longitude = self.extract_coordinates(coord)
			self.description = self.extract_table(desc)
	
	def extract_table(self, elem):
		table_regex = re.compile("(<table.*\/table>)", 
			re.MULTILINE | re.DOTALL)
		match = re.search(table_regex, elem.text)
		if match:
			return match.group(1)
		else:
			return None
	
	def extract_coordinates(self, elem):
		coord_regex = re.compile(
			"([-]?[\d]{1,3}\.[\d]+),([-]?[\d]{1,3}\.[\d]+)",
			re.MULTILINE)
		match = re.search(coord_regex, elem.text)
		if match:
			return (float(match.group(1)), 
				float(match.group(2)))
		else:
			return (0.0, 0.0)
	
	def get_attribute(self, attribute):
		pattern = "%s</td><td.*?>(.*?)</td>" % attribute
		regex = re.compile(pattern, re.MULTILINE | re.DOTALL)
		match = re.search(regex, self.description)
		return match.group(1)

if __name__ == "__main__":
	import kmlparsertests
	kmlparsertests.run_all_tests()

