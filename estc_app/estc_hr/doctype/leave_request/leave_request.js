// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Leave Request", {
    onload(frm){
        if(frm.is_new()){
            
            frappe.call({
                "method": 'estc_app.estc_hr.doctype.employee.employee.get_currency_employee',
                callback: function (r) {
                    frm.set_value('employee',r.message.employee.name)
                    current =new Date();
			        frm.set_value("posting_date", current);
                }
            });
            
            
        }
        
    },
	refresh(frm) {
        if (frm.doc.status=='Draft') {
            frm.set_intro('Please click on <strong>Actions</strong> Menu=><strong>Submit for Approval</strong> to submit your leave request', '#ed246a');
        }
        if (frm.doc.status=='Approved') {
            frm.set_intro('Leave request has been <strong>Approved</strong>', 'green');
        }
        if (frm.doc.status=='Rejected') {
            frm.set_intro('Leave request has been <strong>Rejected</strong>', 'red');
        }

        frm.add_custom_button(__("View Leave Calendar"), () => {
            frappe.set_route("/app/leave-request/view/calendar/default")
        });
      if (frm.is_new()){
        frappe.db.get_value(
            "Fiscal Year",
            {is_default: 1},
            "name"
        ).then(r => {
            console.log(r)
            frm.set_value("fiscal_year", r.message.name);
        })
    }
        
	},
    before_workflow_action: async (frm) => {
        frappe.dom.unfreeze()  
        let promise = new Promise((resolve,reject)=>{
            frappe.confirm("Are you sure you want to <strong>" + frm.selected_workflow_action + '</strong> this request?',
            ()=>resolve(),
            ()=>reject()
            )
         })
         await promise.catch(()=>frappe.throw())

         frappe.show_alert(frm.selected_workflow_action + ' successfully', 5)
    },
    start_date(frm){
        if (frm.doc.start_date && frm.doc.to_date){
            frappe.call({
                args: {
                    "start": frm.doc.start_date,
                    "end": frm.doc.to_date,
                    "fiscal_year":frm.doc.fiscal_year
                },
                method: "estc_app.estc_hr.doctype.leave_request.leave_request.get_leave_count",
                callback: function (r) {
                    frm.doc.total_leave_days = frappe.datetime.get_diff( frm.doc.to_date, frm.doc.start_date ) + 1
                    frm.doc.total_leave_days = frm.doc.total_leave_days - r.message.length
                    if(frm.doc.is_start_date_half_day){
                        frm.doc.total_leave_days = frm.doc.total_leave_days - 0.5
                    }
                    refresh_field('total_leave_days');
                }
            })
            
            
        }  
    },
    to_date(frm){
        frappe.call({
            args: {
                "start": frm.doc.start_date,
                "end": frm.doc.to_date,
                "fiscal_year":frm.doc.fiscal_year
            },
            method: "estc_app.estc_hr.doctype.leave_request.leave_request.get_leave_count",
            callback: function (r) {
                if (frm.doc.start_date && frm.doc.to_date){
                    frm.doc.total_leave_days = frappe.datetime.get_diff(frm.doc.to_date, frm.doc.start_date ) + 1
                    frm.doc.total_leave_days = frm.doc.total_leave_days - r.message.length
                    if(frm.doc.is_to_date_half_day){
                        frm.doc.total_leave_days = frm.doc.total_leave_days - 0.5
                    }
                    refresh_field('total_leave_days');
                }
            }
        })
       
    },
    is_start_date_half_day(frm){
        if(frm.doc.start_date && frm.doc.to_date){
            frm.doc.total_leave_days = frappe.datetime.get_diff( frm.doc.to_date, frm.doc.start_date ) + 1
            if(frm.doc.is_start_date_half_day){
                frm.doc.total_leave_days = frm.doc.total_leave_days - 0.5
            }
            if(frm.doc.is_to_date_half_day){
                frm.doc.total_leave_days = frm.doc.total_leave_days - 0.5
            }
            refresh_field('total_leave_days');
        }
        
    },
    is_to_date_half_day(frm){
        if(frm.doc.start_date && frm.doc.to_date){
            frm.doc.total_leave_days = frappe.datetime.get_diff( frm.doc.to_date, frm.doc.start_date ) + 1
            if(frm.doc.is_to_date_half_day){
                frm.doc.total_leave_days = frm.doc.total_leave_days - 0.5
            }
            if(frm.doc.is_start_date_half_day){
                frm.doc.total_leave_days = frm.doc.total_leave_days - 0.5
            }
            refresh_field('total_leave_days');
        }
        
    }
    
});

