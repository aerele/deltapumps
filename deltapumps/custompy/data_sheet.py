import frappe


@frappe.whitelist()
def make_data_sheet(name):
	quotation = frappe.get_doc("Quotation", name)
	new_datasheet = frappe.db.get_value("Data Sheet", {"quotation": name}) or None
	if new_datasheet:
		return frappe.get_doc("Data Sheet", new_datasheet)
	new_datasheet = frappe.new_doc("Data Sheet")
	new_datasheet.transaction_date=quotation.transaction_date
	new_datasheet.quotation=quotation.name
	new_datasheet.save()
	return new_datasheet

def before_save(self, method):
	if len(self.data_sheet_item) == 0:
		quotation = frappe.get_doc("Quotation", self.quotation)
		for i in quotation.items:
			pb = frappe.db.get_value("Product Bundle", {"new_item_code":i.item_code})
			if pb:
				for j in quotation.packed_items:
					if i.name == j.parent_detail_docname:
						self.append("data_sheet_item",
							{
								"item":j.item_code,
								"item_name":j.item_name,
								"description":j.description,
								"qty":j.qty ,
								"rate":j.rate,
								"amount":j.rate * j.qty ,
								"uom":j.uom,
								"technical_parameter_entry":j.technical_parameter_entry,
								"product_bundle":pb,
								"parent_item":i.item_code
							}
						)
				continue
			self.append("data_sheet_item",
			{
				"item":i.item_code,
				"item_name":i.item_name,
				"qty":i.qty,
				"rate":i.rate,
				"amount":i.amount,
				"uom":i.uom,
				"description":i.customer_description,
				"technical_parameter_entry":i.technical_parameter_entry
			})
	self.item_details = []
	for i in self.data_sheet_item:
		item = frappe.get_doc("Item", i.item)
		for j in frappe.db.get_all("Item Variant Attribute", {"parent": i.item}, "*", order_by="idx"): #item.attributes:
			self.append("item_details", {
				"item": item.name,
				"attribute_category": frappe.db.get_value("Item Attribute", j.attribute, 'attribute_category'),
				"doc_type": "Item Attribute",
				"parameter": j.attribute,
				"parameter_value": j.attribute_value,
				"technical_parameter_entry": i.technical_parameter_entry
			})

		if not i.technical_parameter_entry:
			continue
		parameter_entry =frappe.get_doc("Technical Parameter Entry", i.technical_parameter_entry)
		template = frappe.get_doc("Technical Parameters Template", parameter_entry.technical_parameters_template)
		for j in frappe.db.get_all("Technical Parameters Table", {"parent":i.technical_parameter_entry}, "*", order_by="idx"): #template.technical_parameters_template:
			self.append("item_details", {
				"item": item.name,
				"attribute_category": frappe.db.get_value("Technical Parameters", j.technical_parameter_name, 'attribute_category'),
				"doc_type": "Technical Parameters",
				"parameter": j.technical_parameter_name,
				"parameter_value": frappe.db.get_value("Technical Parameters Table", {"parent":parameter_entry.name, "technical_parameter_name":j.technical_parameter_name}, "parameter_value_as_per_uom") or frappe.db.get_value("Technical Parameters Table", {"parent":parameter_entry.name, "technical_parameter_name":j.technical_parameter_name}, "parameter_value"),
				"parameter_uom": frappe.db.get_value("Technical Parameters Table", {"parent":parameter_entry.name, "technical_parameter_name":j.technical_parameter_name}, "uom") or frappe.db.get_value("Technical Parameters Table", {"parent":parameter_entry.name, "technical_parameter_name":j.technical_parameter_name}, "uom"),
				"remarks": j.remark__notes,
				"technical_parameter_entry": i.technical_parameter_entry
			})


def get_templates(doc):
	data = frappe._dict({})
	for i in doc.data_sheet_item:
		data[i.item+(i.technical_parameter_entry or '')] = {}
		for j in doc.item_details:
			if i.item == j.item:
				if j.technical_parameter_entry:
					if i.technical_parameter_entry != j.technical_parameter_entry:
						continue
				if j.attribute_category == "":
					j.attribute_category = None
				if j.attribute_category in data[i.item+(i.technical_parameter_entry or '')]:
					data[i.item+(i.technical_parameter_entry or '')][j.attribute_category].append([j.parameter, j.parameter_value, j.parameter_uom or '', j.remarks or ''])
				else:
					data[i.item+(i.technical_parameter_entry or '')][j.attribute_category] = [[j.parameter, j.parameter_value, j.parameter_uom or '', j.remarks or '']]
	return data
