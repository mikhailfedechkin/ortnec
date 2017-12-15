import unittest
import mysql.connector
import urllib.request
import lxml.html as html

from selenium import webdriver

# import modules for public selenium grid
import sys

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from testingbotclient import TestingBotClient


class TestEmployeeTable(unittest.TestCase):

	@classmethod
	def setUpClass(self):
		# declare global variables, common properties for TestCase.
		self.DbUserName   = "testcandidate"
		self.DbHost       = "188.166.161.108"
		self.DbName       = "candidate"
		self.DbPassword   = "Ej7mhonxAdHpNoNv"
		self.DbPort       = "3306"

		self.WebPageHost  = "http://benzoelectromoty.ga/qa/"

		self.db_connection = mysql.connector.connect(
									user=self.DbUserName,
									password=self.DbPassword,
	                              	host=self.DbHost,
	                              	database=self.DbName
                      		)

		# Init WebDriver by instruction https://testingbot.com/support/getting-started/pyunit.html
		self.desired_capabilities = webdriver.DesiredCapabilities.CHROME
		self.desired_capabilities['version'] = '62'
		self.desired_capabilities['platform'] = 'WIN10'
		self.desired_capabilities['name'] = 'Testing ortnec with Python'

		self.driver = webdriver.Remote(
			desired_capabilities=self.desired_capabilities,
			command_executor="http://f9f446d0b0e9d941e33438434c9f7a27:7a4f10adb32ba0f8d69012ffdc02c89e@hub.testingbot.com/wd/hub"
		)

		self.driver.implicitly_wait(5)


		#fething data from sources
		self.db_cursor = self.db_connection.cursor()
		self.db_EmployeeTable = self.db_cursor.execute("SELECT * FROM EMPLOYEE;")
		self.db_EmployeeTable = self.db_cursor.fetchall()

		self.db_EmployeeTableDescription = self.db_cursor.execute("DESCRIBE EMPLOYEE;")
		self.db_EmployeeTableDescription = self.db_cursor.fetchall()

		self.db_EmployeeTotalSalary = self.db_cursor.execute("SELECT sum(SALARY) FROM EMPLOYEE;")
		self.db_EmployeeTotalSalary = self.db_cursor.fetchall()


		self.WebPage_Content 	      = urllib.request.urlopen(self.WebPageHost)
		self.WebPage_Object      	  = html.parse(self.WebPage_Content).getroot().xpath(".//*/tr")

		self.WebPage_TableRowNumber   = len(self.WebPage_Object)-2

		self.WebPage_TableRowNames    = self.WebPage_Object[0]

		self.WebPage_TableRows        = self.WebPage_Object[1 : self.WebPage_TableRowNumber+1]
		self.WebPage_TableTotalSalary = self.WebPage_Object[self.WebPage_TableRowNumber+1 : self.WebPage_TableRowNumber+2]

	@classmethod
	def tearDownClass(self):
		self.driver.quit()
		self.db_connection.close()

	#########################################
	def test_CheckFiledsNameCorrectness(self):
		i = 1
		for TableRowName_from_WebPage in self.WebPage_TableRowNames[1:]:
			self.assertEqual(self.db_EmployeeTableDescription[i][0], TableRowName_from_WebPage.text_content(), "ERROR: One or more fields on WebPage has name different with DataBase field")
			i = i + 1

	#########################################
	def test_CheckSizeOfTables(self):
   		self.assertEqual(
   			self.WebPage_TableRowNumber,
   			len(self.db_EmployeeTable),
			"ERROR: Size of tables on WenPage and in DataBase are not the same. Tabse Size on WebPage:"+str(self.WebPage_TableRowNumber)+"  Table size in DataBase:"+str(len(self.db_EmployeeTable))
		)

	#########################################
	def test_CheckDataFieldsCorrectness(self):
		i=0
		j=0

		while i<=self.WebPage_TableRowNumber-1:
			while j<len(self.db_EmployeeTableDescription):
				self.assertEqual(
					str(self.WebPage_TableRows[i][j].text_content()),
					str(self.db_EmployeeTable[i][j]),
					"ERROR: Data on WebPage and into DataBase are not the same. WebPage: |"+str(self.WebPage_TableRows[i][j].text_content())+"| DataBase: |"+str(self.db_EmployeeTable[i][j])+"|"
				)
				j=j+1
			j=0
			i=i+1

	#########################################
	def test_CheckTtlSalaryCorrectness(self):
			self.assertEqual(
					str(self.db_EmployeeTotalSalary[0][0]),
					str(self.WebPage_TableTotalSalary[0][1].text_content()),
					"ERROR: TTL Salary are not the same. OnWebSite: "+str(self.WebPage_TableTotalSalary[0][1].text_content())+" DataBase: |"+str(self.db_EmployeeTotalSalary[0][0])
				)

	#########################################
	def test_CheckTableViaWebDriver(self):
		self.driver.get(self.WebPageHost)
		i = 1

		# Check table fields name
		for TableRowName_from_WebPage in self.driver.find_elements_by_xpath(".//table/thead/tr/th")[1:]:
			self.assertEqual(self.db_EmployeeTableDescription[i][0], TableRowName_from_WebPage.text, "ERROR: One or more fields on WebPage has name different with DataBase field")
			i = i + 1

		i=0
		j=0

		# Check tables fields
		while i<=self.WebPage_TableRowNumber-1:
			while j<len(self.db_EmployeeTableDescription):
				self.assertEqual(
					str(self.driver.find_elements_by_xpath(".//table/tbody/tr["+str(i+1)+"]/td")[j].text),
					str(self.db_EmployeeTable[i][j]),
					"ERROR: Data on WebPage and into DataBase are not the same. WebPage"
				)
				j=j+1
			j=0
			i=i+1

		# Check total salary
		self.assertEqual(
				str(self.db_EmployeeTotalSalary[0][0]),
				str(self.driver.find_elements_by_xpath(".//table/tbody/tr[11]/td")[1].text),
				"ERROR: TTL Salary are not the same. OnWebSite: "+str(self.driver.find_elements_by_xpath('.//table/tbody/tr[11]/td')[1].text)+" DataBase: |"+str(self.db_EmployeeTotalSalary[0][0])
		)


##########################
if __name__ == '__main__':
   unittest.main(warnings='ignore')
