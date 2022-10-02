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

def get_selected_attribs(attributes):
	return [i for i in attributes.split('\n')]

def before_save(self, method):
	for j in self.items:
		if j.item_code:
			bom = frappe.db.get_value("BOM",{"item":j.item_code},"name")
			if bom:
				materials=frappe.get_doc("BOM",bom)
				make_ingreds(self, materials)

def make_ingreds(self,materials):
	for i in materials.items:
		if i.item_code:
			has_bom = frappe.db.get_value("BOM",{"item":i.item_code},"name")
			if has_bom:
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
				})
				bom_doc=frappe.get_doc("BOM",has_bom)
				make_ingreds(self, bom_doc)
			else:
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