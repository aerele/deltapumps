import frappe



@frappe.whitelist()
def make_history_card(name):
	salesorder=frappe.get_doc("Sales Order",name)
	new_hiscard = frappe.db.get_value("History Card", {"sales_order": name}) or None
	if new_hiscard:
		return frappe.get_doc("History Card", new_hiscard)
	new_hiscard = frappe.new_doc("History Card")
	new_hiscard.transaction_date=salesorder.transaction_date
	new_hiscard.sales_order=salesorder.name
	for i in salesorder.items:
		new_hiscard.append("items",
		{
			"item_code":i.item_code,
			"delivery_date":i.delivery_date,
			"item_name":i.item_name,
			"qty":i.qty,
			"rate":i.rate,
			"amount":i.amount,
			"uom":i.uom,
			"description":i.description,
			"technical_parameter_entry":i.technical_parameter_entry
		})
	new_hiscard.save()
	return new_hiscard

@frappe.whitelist()
def get_atribute(name):
	itemcd=frappe.get_doc("Item",name)
	atrib=[]
	for i in itemcd.attributes:
		atrib.append(i.attribute)
	return atrib

@frappe.whitelist()
def get_parameter(parameter):
	if not frappe.db.get_value("Technical Parameter Entry", parameter):
		return []
	parameter_entry = frappe.get_doc("Technical Parameter Entry", parameter)
	return [i.technical_parameter_name for i in parameter_entry.technical_parameter_table]

def get_selected_attribs(attributes, seperator):
	return [i for i in attributes.split(seperator)]

def before_save(self, method):
	for j in self.items:
		if j.item_code:
			bom = frappe.db.get_value("BOM",{"item":j.item_code},"name")
			pb = frappe.db.get_value("Product Bundle", {"new_item_code":j.item_code})
			if bom:
				materials=frappe.get_doc("BOM",bom)
				add_exploded_bom_item(self, materials)
			elif pb:
				pb = frappe.get_doc("Product Bundle", pb)
				add_exploded_pb_item(self, pb)

def add_exploded_pb_item(self, pb):
	for i in pb.items:
		if i.item_code:
			has_pb = frappe.db.get_value("Product Bundle", {"new_item_code":i.item_code})
			rate = frappe.db.get_value("Item Price", {'item_code': i.item_code, "uom":i.uom, "selling":1, "valid_from":["<=", frappe.utils.today()]}, 'price_list_rate')
			if not rate:
				rate = frappe.db.get_value("Item Price", {'item_code': i.item_code, "selling":1, "valid_from":["<=", frappe.utils.today()]}, 'price_list_rate')
			if not rate:
				rate = 0
			self.append("exploded_items",
				{
					"item_code":i.item_code,
					"item_name":frappe.db.get_value("Item", i.item_code, 'item_name'),
					"description":i.description,
					"qty":i.qty,
					"rate":rate,
					"amount":rate * i.qty,
					"uom":i.uom,
					"parent_item":pb.new_item_code
				}
			)
			if has_pb:
				pb_doc = frappe.get_doc("Product Bundle", has_pb)
				add_exploded_pb_item(self, pb_doc)

def add_exploded_bom_item(self,materials):
	for i in materials.items:
		if i.item_code:
			has_bom = frappe.db.get_value("BOM",{"item":i.item_code},"name")
			self.append("exploded_items",
				{
					"item_code":i.item_code,
					"item_name":i.item_name,
					"description":i.description,
					"qty":i.qty,
					"rate":i.rate,
					"amount":i.amount,
					"uom":i.uom,
					"parent_item":materials.item
				}
			)
			if has_bom:
				bom_doc=frappe.get_doc("BOM",has_bom)
				add_exploded_bom_item(self, bom_doc)