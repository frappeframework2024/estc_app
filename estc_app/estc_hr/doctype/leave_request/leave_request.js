// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Leave Request", {
	refresh(frm) {
        if (frm.doc.status=='Draft') {
            frm.set_intro('Please click on <strong>Actions</strong> Menu=><strong>Submit for Approval</strong> to submit your leave request', 'blue');
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
            frm.doc.total_leave_days = frappe.datetime.get_diff( frm.doc.to_date, frm.doc.start_date ) + 1
            if(frm.doc.is_start_date_half_day){
                frm.doc.total_leave_days = frm.doc.total_leave_days - 0.5
            }
            refresh_field('total_leave_days');
        }  
    },
    to_date(frm){
        if (frm.doc.start_date && frm.doc.to_date){
            frm.doc.total_leave_days = frappe.datetime.get_diff( frm.doc.to_date, frm.doc.start_date ) + 1
            if(frm.doc.is_to_date_half_day){
                frm.doc.total_leave_days = frm.doc.total_leave_days - 0.5
            }
            refresh_field('total_leave_days');
        }  
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

