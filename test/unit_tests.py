#!/usr/bin/env python

import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

import unittest
import userapp
import exceptions

class IterableObjectTests(unittest.TestCase):
	def setUp(self):
		self.object=userapp.DictionaryUtility.to_object({
			'user_id':'Bob',
			'properties':{
				'age':{
					'value':154,
					'override':True
				}
			},
			'locks':[
				{
					'issued_by':'locksmith'
				}
			]
		})

	def testIsIterableObject(self):
		self.assertTrue(isinstance(self.object, userapp.IterableObject))
		self.assertTrue(isinstance(self.object.properties, userapp.IterableObject))
		self.assertTrue(isinstance(self.object.locks, list))
		self.assertTrue(isinstance(self.object.locks[0], userapp.IterableObject))

	def testCanGetExistingPropertyValue(self):
		self.assertEqual(self.object.user_id, 'Bob')
		self.assertEqual(self.object['user_id'], 'Bob')

	def testCannotGetNonExistingPropertyValue(self):
		threw_exception=False

		try:
			self.assertEqual(self.object.non_existing_property, 'Bob')
		except exceptions.AttributeError:
			threw_exception=True

		self.assertTrue(threw_exception)

	def testCanSetExistingPropertyValue(self):
		self.object['user_id']='Bob1'
		self.assertEqual(self.object.user_id, 'Bob1')

		self.object.user_id='Bob2'
		self.assertEqual(self.object['user_id'], 'Bob2')

	def testCanGetExistingDeepPropertValue(self):
		self.assertEqual(self.object.properties.age.value, 154)
		self.assertEqual(self.object.properties.age.override, True)

		self.assertEqual(self.object['properties']['age']['value'], 154)
		self.assertEqual(self.object['properties']['age']['override'], True)

	def testCanSetExistingDeepPropertValue(self):
		self.object.properties.age.value=155
		self.object.properties.age.override=False

		self.assertEqual(self.object.properties.age.value, 155)
		self.assertEqual(self.object.properties.age.override, False)

		self.object['properties']['age']['value']=156
		self.object['properties']['age']['override']=True

		self.assertEqual(self.object['properties']['age']['value'], 156)
		self.assertEqual(self.object['properties']['age']['override'], True)

		self.object.properties=None
		self.assertEqual(self.object.properties, None)

	def testCanCheckIfPropertyExists(self):
		self.assertTrue('user_id' in self.object)
		self.assertFalse('user' in self.object)

	def testCanCheckIfDeepPropertyExists(self):
		self.assertTrue('age' in self.object.properties)
		self.assertFalse('age' in self.object.properties.age)

	def testCanIterateAndSwitchPropertyValues(self):
		self.assertEqual(self.object.properties.age.value, 154)
		self.assertEqual(self.object.properties.age.override, True)

		for (key, value) in self.object.properties:
			self.object.properties[key]=value.value

		self.assertEqual(self.object.properties.age, 154)

	def testCanIterateObjectProperties(self):
		iterations=0

		for (key, value) in self.object:
			self.assertEqual(key, ['locks','user_id','properties'][iterations])
			iterations += 1

		self.assertEqual(iterations, 3)

	def testCanSerializeToJson(self):
		self.assertEqual(self.object.to_json(), '{"locks": [{"issued_by": "locksmith"}], "user_id": "Bob", "properties": {"age": {"override": true, "value": 154}}}')

def main():
	unittest.main()

if __name__ == '__main__':
	main()