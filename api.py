# test

import frappe
import json
from datetime import datetime
# from erpnext.accounts.doctype.payment_request.payment_request import make_payment_request, make_payment_entry
from frappe import DoesNotExistError
from erpnext.selling.doctype.sales_order.sales_order import make_sales_invoice
from erpnext.accounts.doctype.payment_request.payment_request import (
    make_payment_request,
    make_payment_entry,
)

SUCCESS = 200
NOT_FOUND = 400

@frappe.whitelist()
def gforms_integ(fname,mname,lname,gender,contact_num,email,landline,emer_cont_person, emer_cont_num,whatsapp,city,state,country,territory):
    add_item = frappe.get_doc({
        "doctype": "Lead",
        "first_name": fname,
        "middle_name":mname,
        "last_name": lname,
        "gender": gender,
        "mobile_no": contact_num, 
        "email_id": email,
        "phone": landline,
        "emergency_contact": emer_cont_person,
        "phone_ext":emer_cont_num,
        "whatsapp_no":whatsapp,
        "city":city,
        "state": state,
        "country": country,
        "territory": territory if territory else "Philippines"
        # "bdate": bdate,
        # "req_movein_date": req_movein_date,
        # "eme_contact_name": eme_contact_name,
    })

    # NOTE: Lease Application doctype is new

    add_item.insert()
    frappe.db.commit()

    return add_item

# @frappe.whitelist(allow_guest=True)
def get_all_items():
    items = frappe.db.sql("""SELECT * from `tabItem`;""")

@frappe.whitelist()
def add_test_buy():
    add_item = frappe.get_doc({
        "doctype": "My Test Buy Doctype",
        "item": "API Item 1",
        "price_test": 200.50
    })
    add_item.insert()
    frappe.db.commit()

    return add_item

@frappe.whitelist()
def new_customer_from_lead(name):
    try:
        lead = frappe.get_doc("Lead", name)
        
        # exist_customer = frappe.get_doc("Customer",lead.lead_name) 
        # if not exist_customer:
        customer = frappe.new_doc("Customer")
        customer.lead_name = name
        customer.customer_name = lead.lead_name
        customer.salutation = lead.salutation
        customer.territory = lead.territory
        customer.gender = lead.gender
        customer.customer_group = "Individual"
        customer.tenant_email = lead.email_id
        customer.payment_methods = "gcash"

        customer.insert()
        
        # contact = frappe.get_all("Contact",filters={"email_id": lead['email_id']}, fields=["name"])
        
        # if contact:
        #     for email in contact:
        #         frappe.db.set_value("Customer", lead.lead_name , "customer_primary_contact", email['name'])
        # else:
        #     frappe.msgprint("Customer Already Exist")


        # lead.customer = customer.name
        # lead.save()

    except Exception as e:
          return "Failed to Insert Customer."
@frappe.whitelist()
def delete_customer(name):
    try:
        frappe.delete_doc("Customer",name)
        # frappe.delete_doc("Contact",contact_email)
    except Exception as e:
        return "Failed to Delete Customer." 
    

@frappe.whitelist()
def get_property_name():
    property_detail = frappe.get_list("Lease", fields=['lease_customer','property'])
    return property_detail

@frappe.whitelist()
def get_reading_detail():
    list = frappe.get_all(
        "Meter Reading Detail", 
        fields=["Property","meter_number","current_meter_reading","previous_meter_reading","reading_difference"], 
        filters={
             "parenttype": "Meter Reading"
        },
        order_by="idx"
    )
    return list


@frappe.whitelist()
def get_subscription_data():
    try:
         lists = frappe.db.get_list('Subscription',

            fields=['name','party', 'property'],
        )
         return lists
    
    except Exception as e:
        frappe.throw(_("DocType not Fount"))


@frappe.whitelist()
def update_sub_plan_meter_qt(reading_detail):

    try:

        plans = frappe.get_all(
            "Subscription Plan Detail", 
            fields=["*"], 
            filters={
                "parenttype": "Subscription",
            },
            order_by="idx"
        )
        python_list = json.loads(reading_detail)
        
        for reading in python_list:
            for plan in plans:
                if reading["name"] == plan['parent'] and reading['meter_type'] == plan['plan']:
                    doc = frappe.get_doc("Subscription Plan Detail", plan["name"])
                    doc.qty = reading['reading_diff']
                    doc.save()
                    frappe.db.commit()

        return plans
    except Exception as e:
        frappe.throw(_("DocType not Fount"))

@frappe.whitelist()
def get_payment_method():
    default_payment_method = frappe.get_value("Customer", "Administrator", "payment_methods")
    get_payment_method = frappe.get_value("PayMongo Payment Method",default_payment_method, ['fee', 'payment_method'])
    
    return get_payment_method

@frappe.whitelist()
def create_payment_entry():
    try:
        payment_entry = frappe.get_doc(make_payment_entry("ACC-PRQ-2023-00073"))
        payment_entry.submit()
    except DoesNotExistError:
        print("The document does not exist.")
    
    
def webhook_error(error, ptype):
      
    paymongo_logs = frappe.get_doc({
        "doctype" : "Paymongo Logs",
        "push_type" : ptype,
        "paymongo_message" : error,
    })
    paymongo_logs.insert()
    frappe.db.commit()
    
    return paymongo_logs

def _payment_entry(reference_number):

    # id = str(reference_number)
    try:
        payment_entry = frappe.get_doc(make_payment_entry(docname=reference_number))
        webhook_error(payment_entry,'payment entry')
        payment_entry.insert(ignore_permissions=True)
        payment_entry.submit()
        webhook_error(payment_entry,'payment entry 2')
        frappe.db.commit()
        webhook_error(payment_entry,'payment entry 4')
    except Exception as e:
        webhook_error(e,'payment entry error')



@frappe.whitelist(allow_guest=True)
def paymongo_log():

    req = ''
    if frappe.request.data != b'':
        try:
            req = json.loads(frappe.request.data)
            webhook_error(json.dumps(req),"object data") #14
        except Exception as e:
            webhook_error(e,'webhook error')
    else :
        webhook_error("Executed but Somethong went wrong!!",'webhook error') 

   
    if(req['data']['id']):
        status = req['data']['attributes']['data']['attributes']['payments'][0]['attributes']['status']
        if status == "paid":
            reference_number = req['data']['attributes']['data']['attributes']['reference_number']
            webhook_error(reference_number, "Data Found")#15
            _payment_entry(reference_number)
        
            # return update_invoice(reference_number,"Update Invoice")
        else:
            webhook_error("Status not found", "Missing data")
    else:
        webhook_error("data not found","webhook error") #16
    

    return { "status_code" : 200 }

@frappe.whitelist()
def get_unpaid_balance(customer_name):
    try:
        ledger_entries = frappe.get_all('GL Entry', filters={'party_type': 'Customer', 'party': customer_name},fields=['debit', 'credit'])
        balance = sum( entry['debit'] - entry['credit'] for entry in ledger_entries)
        return balance
    except Exception as e:
        frappe.throw(_("DocType not Fount"))