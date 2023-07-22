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
	if len(self.items) == 0:
		salesorder=frappe.get_doc("Sales Order",self.sales_order)
		for i in salesorder.items:
			pb = frappe.db.get_value("Product Bundle", {"new_item_code":i.item_code})
			if pb:
				for j in salesorder.packed_items:
					if i.name == j.parent_detail_docname:
						self.append("items",
							{
								"item_code":j.item_code,
								"item_name":j.item_name,
								"description":j.description,
								"qty":j.qty,
								"rate":j.rate,
								"amount":j.rate * j.qty,
								"uom":j.uom,
								"technical_parameter_entry":j.technical_parameter_entry,
								"product_bundle":pb,
								"parent_item":i.item_code
							}
						)
				continue
			self.append("items",
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
	if len(self.exploded_items) == 0:
		for j in self.items:
			if j.item_code:
				bom = frappe.db.get_value("BOM",{"item":j.item_code, "docstatus":1, "is_default":1},"name")
				if bom and not j.do_not_explode:
					materials=frappe.get_doc("BOM",bom)
					add_exploded_bom_item(self, materials)

def add_exploded_bom_item(self,materials):
	for i in materials.items:
		if i.item_code:
			has_bom = frappe.db.get_value("BOM",{"item":i.item_code, "docstatus":1, "is_default":1},"name")
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
			if has_bom and not i.do_not_explode:
				bom_doc=frappe.get_doc("BOM",has_bom)
				add_exploded_bom_item(self, bom_doc)