import frappe


@frappe.whitelist()
def make_data_sheet(name):
	quotation = frappe.get_doc("Quotation", name)
	new_datasheet = frappe.db.get_value("Data Sheet", {"quotation": name}) or None
	if new_datasheet:
		return frappe.get_doc("Data Sheet", new_datasheet)
	new_datasheet = frappe.new_doc("Data Sheet")
	new_datasheet.transaction_date=quotation.transaction_date
	new_datasheet.sales_order=quotation.name
	for i in quotation.items:
		new_datasheet.append("data_sheet_item",
		{
			"item_code":i.item_code,
			"item_name":i.item_name,
			"qty":i.qty,
			"rate":i.rate,
			"amount":i.amount,
			"uom":i.uom,
			"description":i.description,
			"technical_parameter_entry":i.technical_parameter_entry
		})
	for i in new_datasheet.data_sheet_item:
		item = frappe.get_doc("Item", i.item_code)
		for j in item.attributes:
			new_datasheet.append("item_details", {
				"item": item.name,
				"attribute_category": frappe.db.get_value("Item Attribute", j.attribute, 'attribute_category'),
				"doc_type": "Item Attribute",
				"parameter": j.attribute,
				"parameter_value": j.attribute_value
			})
		parameter_entry =frappe.get_doc("Technical Parameter Entry", i.technical_parameter_entry)
		for j in parameter_entry.technical_parameter_table:
			new_datasheet.append("item_details", {
				"item": item.name,
				"attribute_category": frappe.db.get_value("Technical Parameters", j.technical_parameter_name, 'attribute_category'),
				"doc_type": "Item Attribute",
				"parameter": j.technical_parameter_name,
				"parameter_value": j.parameter_value_as_per_uom or j.parameter_value
			})
	new_datasheet.save()
	return new_datasheet