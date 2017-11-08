from datetime import date
import json

class Wit(object):
	def __init__(self, json_content):

		for key, value in json_content.items():
			setattr(self, key, value)

		self.parent=None
		self.children={}
	
	def get_id(self):
		return getattr(self, 'id')

	def get_attr(self, attr):
		try: 
			return getattr(self, attr)
		except:
			return "undefined"

	def set_parent(self, parent):
		self.parent = parent

	def get_parent(self):
		return self.parent

	def get_child(self,wit_id):
		return self.children[wit_id]

	def get_children(self):
		return self.children.values()

	def add_child(self, child):
		self.children[child.get_id()] = child
		child.set_parent(parent=self)

	def add_descendant(self, parent_id, child):
		if self.get_id() == parent_id:
			self.add_child(child)
			return self

		for wit in self.get_children() :
			found_dad = wit.add_descendant(parent_id = parent_id, child = child)
			if found_dad: return found_dad

		return None

	def get_descendant(self, child_id):
		if self.get_id() == child_id:
			return self

		for wit in self.get_children() :
			found_child = wit.get_descendant(child_id = child_id)
			if found_child: return found_child

		return None

	def update(self, json_content):
		for key, value in json_content.items():
			if key not in ('id', 'url'):
				setattr(self, key, value)

	def update_all(self, json_table):	
		for each in json_table:
			self.get_descendant(each['id']).update(json_content = each['fields'])

	def to_dict(self):
		return self.__dict__

	def __repr__(self):
		parent = "None"
		children = " / "
		if self.get_parent(): parent = self.get_parent().get_id()
		for child in self.get_children(): 
			children +=  child.__repr__()
		return "WIT with id = %s, parent id = %s, children id = %s"%(self.get_id(), parent, children)
