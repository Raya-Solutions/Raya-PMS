# -*- coding: utf-8 -*-
# Copyright (c) 2018, Aakvatech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import add_days, today, getdate, add_months, get_datetime, now, date_diff
from propms.auto_custom import app_error_log

class Exit(Document):
    # pass 
    def before_save(self):
           lease = frappe.db.get_all('Lease', filters={'name': self.lease ,'lease_status': ['=',['On Lease', 'Off lease in 3 months']]}, fields = ['property'])
           for property in lease:
            frappe.db.set_value("Property",property['property'], "status", "Available")
           
    def validate(self):
        try:
            # if (
            #     get_datetime(self.start_date)
            #     <= get_datetime(now())
            #     <= get_datetime(add_months(self.end_date, -3))
            # ):
             
                
                frappe.db.set_value("Lease", self.lease , "lease_status", "Closed")
                # frappe.db.set_value("Property","Test Property 4", "status", "Available")
                
                
            # if (
            #     get_datetime(add_months(self.end_date, -3))
            #     <= get_datetime(now())
            #     <= get_datetime(add_months(self.end_date, 3))
            # ):
            #     frappe.db.set_value(
            #         "Property", self.property, "status", "Off Lease in 3 Months"
            #     )
            #     frappe.msgprint("Property set to Off Lease in 3 Months")
        except Exception as e:
            app_error_log(frappe.session.user, str(e))
