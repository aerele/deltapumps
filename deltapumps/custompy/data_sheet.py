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
	for i in quotation.items:
		new_datasheet.append("data_sheet_item",
		{
			"item":i.item_code,
			"item_name":i.item_name,
			"qty":i.qty,
			"rate":i.rate,
			"amount":i.amount,
			"uom":i.uom,
			"description":i.description,
			"technical_parameter_entry":i.technical_parameter_entry
		})
		if frappe.db.get_value("Product Bundle",i.item_code,"name"):
			pbi = frappe.get_doc("Product Bundle",i.item_code)
			for j in pbi.items:
				rate = frappe.db.get_value("Item Price", {'item_code': i.item_code, "uom":i.uom, "selling":1, "valid_from":["<=", frappe.utils.today()]}, 'price_list_rate')
				if not rate:
					rate = frappe.db.get_value("Item Price", {'item_code': i.item_code, "selling":1, "valid_from":["<=", frappe.utils.today()]}, 'price_list_rate')
				if not rate:
					rate = 0
				new_datasheet.append("data_sheet_item",
						{
							"item":j.item_code,
							"item_name":frappe.db.get_value("Item", i.item_code, 'item_name'),
							"qty":j.qty,
							"rate":rate,
							"amount":rate * j.qty,
							"uom":j.uom,
							"description":j.description,
							"technical_parameter_entry":'', #j.technical_parameter_entry,
							"parent_item":i.item_code
						})
	for i in new_datasheet.data_sheet_item:
		item = frappe.get_doc("Item", i.item)
		for j in item.attributes:
			new_datasheet.append("item_details", {
				"item": item.name,
				"attribute_category": frappe.db.get_value("Item Attribute", j.attribute, 'attribute_category'),
				"doc_type": "Item Attribute",
				"parameter": j.attribute,
				"parameter_value": j.attribute_value
			})

		if not i.technical_parameter_entry:
			continue
		parameter_entry =frappe.get_doc("Technical Parameter Entry", i.technical_parameter_entry)
		template = frappe.get_doc("Technical Parameters Template", parameter_entry.technical_parameters_template)
		for j in template.technical_parameters_template:
			new_datasheet.append("item_details", {
				"item": item.name,
				"attribute_category": frappe.db.get_value("Technical Parameters", j.technical_parameter_name, 'attribute_category'),
				"doc_type": "Technical Parameters",
				"parameter": j.technical_parameter_name,
				"parameter_value": frappe.db.get_value("Technical Parameters Table", {"parent":parameter_entry.name, "technical_parameter_name":j.technical_parameter_name}, "parameter_value_as_per_uom") or frappe.db.get_value("Technical Parameters Table", {"parent":parameter_entry.name, "technical_parameter_name":j.technical_parameter_name}, "parameter_value")
			})


	new_datasheet.save()
	return new_datasheet


def get_templates(doc):
	data = frappe._dict({})
	for i in doc.data_sheet_item:
		data[i.item] = {}
		for j in doc.item_details:
			if i.item == j.item:
				if j.attribute_category in data[i.item]:
					data[i.item][j.attribute_category].append([j.parameter, j.parameter_value])
				else:
					data[i.item][j.attribute_category] = [[j.parameter, j.parameter_value]]
	return data
