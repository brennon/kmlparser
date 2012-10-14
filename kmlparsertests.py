from unittest import *
from kmlparser import *
import xml.etree.ElementTree
import shutil

class KMLParserManagerTestCase(TestCase):
	
	def test_instantiation(self):
		pm = KMLParserManager()
		self.assertIsNotNone(pm, msg="Cannot instantiate KMLParserManager")
	
	def test_add_parser(self):
		pm = KMLParserManager()
		p = KMLParser(filename="root.kml")
		pm.add_parser(p)
		self.assertTrue(p in pm.parsers)
	
	def test_add_parser_with_link(self):
		pm = KMLParserManager()
		p = KMLParser(filename="root.kml")
		pm.add_parser(p)
		new_link = "http://geospatial.dcgis.dc.gov/dc_kmz/"
		new_link += "Business_and_Economic_Development/"
		new_link += "DCG9_Miscellaneous_ABRALicensePt/"
		new_link += "DCG9_Miscellaneous_ABRALicensePt/"
		new_link += "DCG9_Miscellaneous_ABRALicensePt.kmz"
		self.assertTrue(new_link in pm.pending_links)
	
	def test_all_placemarks(self):
		pm = KMLParserManager()
		p = KMLParser(filename="one_placemark.kml")
		pm.add_parser(p)
		pm.explore_all()
		marks = pm.all_placemarks()
		self.assertEqual(pm.placemarks[0].latitude, -76.9900360306117)
	
	def test_explore_all(self):
		p = KMLParser(filename="root.kml")
		pm = KMLParserManager()
		pm.add_parser(p)
		self.assertEqual(len(pm.explored_links), 0)
		pm.explore_all()
		self.assertTrue(len(pm.explored_links) > 40)
	
class KMLParserTestCase(TestCase):
	
	def test_instantiation(self):
		self.assertRaises(ValueError, KMLParser)
	
	def test_instantiation_filename(self):
		p = KMLParser(filename="root.kml")
		self.assertIsNotNone(p, msg="Cannot instantiate KMLParser")
	
	def test_instantiation_url(self):
		link = "https://developers.google.com/"
		link += "kml/documentation/KML_Samples.kml"
		p = KMLParser(url=link)
		self.assertIsNotNone(p, msg="Cannot instantiate KMLParser")
	
	def test_instantiation_bad_url(self):
		link = "http://thisisabaddomain.extension/badfile.bad"
		self.assertRaises(IOError, 
			KMLParser,
			url=link)
	
	def test_instantiation_file_and_link(self):
		link = "https://developers.google.com/"
		link += "kml/documentation/KML_Samples.kml"
		self.assertRaises(ValueError, 
			KMLParser,
			filename="root.kml",
			url=link)
	
	def test_parse_input(self):
		p = KMLParser(filename="root.kml")
		self.assertIsInstance(p.tree, xml.etree.ElementTree.ElementTree)
	
	def test_parse_file(self):
		p = KMLParser(filename="root.kml")
		kml_file = open("root.kml", "r")
		parsed = p.parse_kml_file(kml_file)
		self.assertIsInstance(parsed, xml.etree.ElementTree.ElementTree)
		file.close(kml_file)
	
	def test_fetch_network_file(self):
		p = KMLParser(filename="root.kml")
		link = "https://developers.google.com/"
		link += "kml/documentation/KML_Samples.kml"
		result = p.fetch_remote_file(link)
		self.assertIsInstance(result, str)
		shutil.rmtree(os.path.dirname(result))
	
	def test_parse_network_kml(self):
		link = "https://developers.google.com/"
		link += "kml/documentation/KML_Samples.kml"
		p = KMLParser(url=link)
		self.assertIsInstance(p.tree, xml.etree.ElementTree.ElementTree)
	
	def test_parse_network_kmz(self):
		link = "http://dl.google.com/developers/maps/buffetthawaiitour.kmz"
		p = KMLParser(url=link)
		self.assertIsInstance(p.tree, xml.etree.ElementTree.ElementTree)
	
	def test_network_links(self):
		p = KMLParser(filename="root.kml")
		new_link = "http://geospatial.dcgis.dc.gov/dc_kmz/"
		new_link += "Business_and_Economic_Development/"
		new_link += "DCG9_Miscellaneous_ABRALicensePt/"
		new_link += "DCG9_Miscellaneous_ABRALicensePt/"
		new_link += "DCG9_Miscellaneous_ABRALicensePt.kmz"
		links = p.network_links()
		self.assertEqual(links[0], new_link)
	
	def test_namespace(self):
		p = KMLParser(filename="root.kml")
		self.assertEqual(p.namespace, 
			"{http://www.opengis.net/kml/2.2}", 
			msg="Namespace not extracted")
	
	def test_extract_network_link_url(self):
		p = KMLParser(filename="root.kml")
		network_link = p.tree.findall("%sNetworkLink" % p.namespace)
		url = p.extract_network_link_url(network_link[0])
		actual = "http://geospatial.dcgis.dc.gov/dc_kmz/"
		actual += "Business_and_Economic_Development/"
		actual += "DCG9_Miscellaneous_ABRALicensePt/"
		actual += "DCG9_Miscellaneous_ABRALicensePt/"
		actual += "DCG9_Miscellaneous_ABRALicensePt.kmz"
		self.assertEqual(url, actual)
	
	def test_parse_filename_from_url(self):
		url = "http://www.brennnonbortz.com/subdir/myfile.txt"
		filename = KMLParser.parse_filename_from_url(url)
		self.assertEqual(filename, "myfile.txt", 
			msg="Filename not extracted correctly")
		url = "http://www.brennnonbortz.com/subdir/"
		filename = KMLParser.parse_filename_from_url(url)
		self.assertEqual(filename, None, 
			msg="Filename not extracted correctly")
	
	def test_placemarks(self):
		p = KMLParser(filename="one_placemark.kml")
		tree = xml.etree.ElementTree.parse("one_placemark.kml")
		elem = tree.find(".//{http://www.opengis.net/kml/2.2}Placemark")
		placemark = KMLPlacemark(element=elem)
		self.assertEqual(p.placemarks()[0].latitude, placemark.latitude)
		self.assertEqual(p.placemarks()[0].longitude, placemark.longitude)
		self.assertEqual(p.placemarks()[0].description, placemark.description)
	
class KMLPlacemarkTestCase(TestCase):
	
	def test_instantiation(self):
		p = KMLPlacemark()
		self.assertIsNotNone(p, msg="Cannot instantiate KMLPlacemark")
	
	def test_initial_values(self):
		p = KMLPlacemark()
		self.assertEqual(p.latitude, 0.0)
		self.assertEqual(p.longitude, 0.0)
		self.assertEqual(p.description, None)
	
	def test_instantiation_with_kml(self):
		tree = xml.etree.ElementTree.parse("one_placemark.kml")
		elem = tree.find(".//{http://www.opengis.net/kml/2.2}Placemark")
		coord = elem.find(".//{http://www.opengis.net/kml/2.2}coordinates")
		desc = elem.find(".//{http://www.opengis.net/kml/2.2}description")
		placemark = KMLPlacemark(element=elem)
		table = """<table class="dataGrid" width="100%"><tr><td class="dataGridLeftTD">LICENSE NUMBER</td><td class="dataGridRightTD">ABRA-074804</td></tr><tr><td class="dataGridLeftTD">APPLICANT</td><td class="dataGridRightTD">SWL Liquors, Inc.</td></tr><tr><td class="dataGridLeftTD">TRADE NAME</td><td class="dataGridRightTD">Wheeler Liquors</td></tr><tr><td class="dataGridLeftTD">LICENSE DESCRIPTION</td><td class="dataGridRightTD">Retailer A</td></tr><tr><td class="dataGridLeftTD">ADDRESS</td><td class="dataGridRightTD">4137 WHEELER ROAD SE</td></tr></table><table border="0" width="100%"><tr><td><img src="http://geospatial.dcgis.dc.gov/DC_KMZ/dclogo.gif"  alt="DCGIS" border="none" /></td><td class="ProvidedBy" style="text-align: right">Provided By:</td><td class="bottomLinks"><a href='http://dcgis.dc.gov' target='_blank' >DC GIS</a></td></tr></table>"""
		self.assertEqual(placemark.description, table)
		self.assertEqual(placemark.latitude, -76.9900360306117)
		self.assertEqual(placemark.longitude, 38.8334126374051)
	
	def test_extract_table(self):
		tree = xml.etree.ElementTree.parse("one_placemark.kml")
		elem = tree.find(".//{http://www.opengis.net/kml/2.2}Placemark")
		desc = elem.find(".//{http://www.opengis.net/kml/2.2}description")
		table = """<table class="dataGrid" width="100%"><tr><td class="dataGridLeftTD">LICENSE NUMBER</td><td class="dataGridRightTD">ABRA-074804</td></tr><tr><td class="dataGridLeftTD">APPLICANT</td><td class="dataGridRightTD">SWL Liquors, Inc.</td></tr><tr><td class="dataGridLeftTD">TRADE NAME</td><td class="dataGridRightTD">Wheeler Liquors</td></tr><tr><td class="dataGridLeftTD">LICENSE DESCRIPTION</td><td class="dataGridRightTD">Retailer A</td></tr><tr><td class="dataGridLeftTD">ADDRESS</td><td class="dataGridRightTD">4137 WHEELER ROAD SE</td></tr></table><table border="0" width="100%"><tr><td><img src="http://geospatial.dcgis.dc.gov/DC_KMZ/dclogo.gif"  alt="DCGIS" border="none" /></td><td class="ProvidedBy" style="text-align: right">Provided By:</td><td class="bottomLinks"><a href='http://dcgis.dc.gov' target='_blank' >DC GIS</a></td></tr></table>"""
		placemark = KMLPlacemark()
		extracted = placemark.extract_table(desc)
		self.assertEqual(table, extracted)
	
	def test_extract_coordinates(self):
		tree = xml.etree.ElementTree.parse("one_placemark.kml")
		elem = tree.find(".//{http://www.opengis.net/kml/2.2}Placemark")
		coord = elem.find(".//{http://www.opengis.net/kml/2.2}coordinates")
		placemark = KMLPlacemark()
		latitude, longitude = placemark.extract_coordinates(coord)
		self.assertEqual(latitude, -76.9900360306117)
		self.assertEqual(longitude, 38.8334126374051)
	
	def test_extract_attribute(self):
		tree = xml.etree.ElementTree.parse("one_placemark.kml")
		elem = tree.find(".//{http://www.opengis.net/kml/2.2}Placemark")
		coord = elem.find(".//{http://www.opengis.net/kml/2.2}coordinates")
		desc = elem.find(".//{http://www.opengis.net/kml/2.2}description")
		placemark = KMLPlacemark(element=elem)
		name = placemark.get_attribute("TRADE NAME")
		number = placemark.get_attribute("LICENSE NUMBER")
		applicant = placemark.get_attribute("APPLICANT")
		license_desc = placemark.get_attribute("LICENSE DESCRIPTION")
		address = placemark.get_attribute("ADDRESS")
		self.assertEqual(name, "Wheeler Liquors")
		self.assertEqual(number, "ABRA-074804")
		self.assertEqual(applicant, "SWL Liquors, Inc.")
		self.assertEqual(license_desc, "Retailer A")
		self.assertEqual(address, "4137 WHEELER ROAD SE")
		
	
def run_all_tests():
	loader = TestLoader()
	
	suite = loader.loadTestsFromTestCase(KMLPlacemarkTestCase)
	# suite.addTests(loader.loadTestsFromTestCase(KMLParserTestCase))
	# suite.addTests(loader.loadTestsFromTestCase(KMLParserManagerTestCase))
	
	runner = TextTestRunner(verbosity=2)
	result = runner.run(suite)

if __name__ == "__main__":
	run_all_tests()

