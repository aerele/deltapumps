import frappe



@frappe.whitelist()
def make_history_card(name):
	salesorder=frappe.get_doc("Sales Order",name)
	new_hiscard=frappe.new_doc("History Card")
	new_hiscard.transaction_date=salesorder.transaction_date
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
	return new_hiscard

@frappe.whitelist()
def get_atribute(name):
	itemcd=frappe.get_doc("Item",name)
	atrib=[]
	for i in itemcd.attributes:
		atrib.append(i.attribute)
	return atrib


def before_save(self):
	for j in self.items:
		if j.item_code:
			bom = frappe.db.get_value("BOM",{"item":j.item_code},"name")
			if bom:
				ingred=frappe.get_doc("BOM",bom)
				self.pname=ingred.item_name
				self.make_ingreds(ingred)

def make_ingreds(self,ingred):
	for i in ingred.items:
		if i.item_code:
			bom1 = frappe.db.get_value("BOM",{"item":i.item_code},"name")
			if bom1:
				self.append("ingredients",
				{
					"item_code":i.item_code,
					"item_name":i.item_name,
					"description":i.description,
					"qty":i.qty,
					"rate":i.rate,
					"amount":i.amount,
					"uom":i.uom,
					"parent_item":self.pname
				})
				bomdoc=frappe.get_doc("BOM",bom1)
				self.make_ingreds(bomdoc)
			else:
				self.append("ingredients",
				{
					"item_code":i.item_code,
					"item_name":i.item_name,
					"description":i.description,
					"qty":i.qty,
					"rate":i.rate,
					"amount":i.amount,
					"uom":i.uom,
					"parent_item":self.pname
				}
		)