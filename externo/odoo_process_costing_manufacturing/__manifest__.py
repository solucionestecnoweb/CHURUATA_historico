# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Process Costing in Manufacturing Process',
    'version': '2.2.1.7',
    'category' : 'Manufacturing',
    'license': 'Other proprietary',
    'price': 99.0,
    'currency': 'EUR',
    'summary': """This app allow you to do process costing (Material Cost, Labour Cost, Overheads) for manufacturing orders.""",
    'depends': [
            'mrp',
            'stock',
            'sales_team',
            'l10n_ve_fiscal_requirements',
    ],
    'description': """
Odoo Process Costing Manufacturing
Direct Overhead Cost
Workorder
Manufacturing order
production order
Process Costing in Manufacturing
process costing
Material Cost
Direct Labour Cost
Labour Cost
Overheads Cost
Bill of Materials - Direct Material Cost
Bill of Materials
​process costing
process costing manufacturing
process costing production
manufacturing cost
manufacturing costing
manufacturing labour
manufacturing direct material
manufacturing material cost
manufacturing overhead
manufacturing overheads
manufacturing product cost
manufacturing unit cost
process costing example
process costing mrp
mrp process costing
mrp project order sheet
manufacturing costing method 
process costing sheet
Odoo process costing And process costing Sheet (Contracting)
Odoo process costing sheet
process costing sheet odoo
contracting odoo
odoo manufacturing
process costing (Contracting)
odoo process costing (Contracting)
odoo process costing Contracting
job order odoo
production costing
mrp costing
material costing
direct material
indirect material
overhead costing
labour costing
labour cost
material cost
producted cost
production mrp costing
job costing
job cost sheet
job contracting
contract costing
work order odoo
job Contracting
process costing
process costing Contracting
odoo Contracting
Contracting odoo job
Jobs
Jobs/Configuration
Jobs/Configuration/Job Types
Jobs/Configuration/Stages
Jobs/Job Costs
Jobs/Job Costs/process costing Sheets
Jobs/Job Orders
Jobs/Job Orders/Job Notes
Jobs/Job Orders/Job Orders
Jobs/Job Orders/Project Issues
BOQ
process costing
Notes
Project Report
Task Report
Jobs/Materials / BOQ 
Jobs/Materials / BOQ /Material Requisitions/ BOQ
Jobs/Materials / BOQ /Materials
Jobs/Projects
Jobs/Projects/Project Budgets
Jobs/Projects/Project Notes
Jobs/Projects/Projects
Jobs/Sub Contractors 
Jobs/Sub Contractors /Sub Contractors
material requision odoo
Contracting
job Contracting
job sheet
process costing Contracting
process costing plan
costing
cost Contracting
subcontracting
Email: contact@probuse.com for more details.
This module provide manufacturing Management Related Activity.
manufacturing
manufacturing Projects
Budgets
Notes
Materials
Material Request For Job Orders
Add Materials
Job Orders
Create Job Orders
Job Order Related Notes
Issues Related Project
Vendors
Vendors / Contractors

manufacturing Management
manufacturing Activity
manufacturing Jobs
Job Order manufacturing
Job Orders Issues
Job Order Notes
manufacturing Notes
Job Order Reports
manufacturing Reports
Job Order Note
manufacturing app
manufacturing 
manufacturing costing
manufacturing product cost
finished product cost
product costing process
manufacturing Management

This module provide feature to manage manufacturing Management activity.
manufacturing
manufacturing/Configuration
manufacturing/Configuration /Stages
manufacturing/manufacturing
manufacturing/manufacturing/Budgets
manufacturing/manufacturing/Notes
manufacturing/manufacturing/Projects
manufacturing/Job Orders
manufacturing/Job Orders /Issues
manufacturing/Job Orders /Job Orders
manufacturing/Job Orders /Notes
manufacturing/Materials / BOQ
manufacturing/Materials /Material Requisitions / BOQ
manufacturing/Materials /Materials
manufacturing/Vendors
manufacturing/Vendors /Contractors
Defined Reports
Notes
Project Report
Task Report
manufacturing Project - Project Manager
real estate property
propery management
bill of material
Material Planning On Job Order

Bill of Quantity On Job Order
Bill of Quantity manufacturing
process costing
process costing sheet
cost sheet
project cost sheet
project planning
project sheet cost
process costing plan
manufacturing cost sheet
manufacturing process costing sheet
manufacturing jobs
manufacturing job sheet
manufacturing material
manufacturing labour
manufacturing overheads
manufacturing sheet plan
costing
workshop
job workshop
workshop
jobs
cost centers
manufacturing purchase order
manufacturing activities
Basic process costing
process costing Example
job order costing
job order
job orders
Tracking Labor
Tracking Material
Tracking Overhead
overhead
material plan
job overhead
job labor
process costing Sheet
Example For Larger Job
process costing is a method of costing applied in industries where production is measured in terms of completed jobs. Industries where process costing is generally applied are Printing Press. Automobile Garage, Repair workshops, Ship Building, Foundry and other similar manufacturing units which manufacture to customers� specific requirements.

process costing is a method of costing whereby cost is compiled for a job or work order. The production is against customer�s orders and not for stock. The cost is not related to the unit of production but is a cost for the job, e. g printing of 5000 ledger sheets, repairs of 50 equipment�s, instead of printing one sheet or repair of one equipment.

The elements of cost comprising Prime Cost viz. direct materials, direct labour and direct expenses are charged directly to the jobs concerned, the overhead charged to a job is an apportioned portion of the departmental overhead.
Advantages of Job Order Costing

Features of process costing
Enabling process costing
Creating Cost Centers for process costing
project process costing
project process costing
project job contracting
project job contract
job contract
jobs contract
manufacturing
manufacturing app
manufacturing odoo
odoo manufacturing
Create Project/Contract -> Create Job Orders -> Create Multiple process costing Sheets under Same Project -> Plan your materials, labour and overhead for each Jobs -> View of Planned and Actual Amount/Qty by each Cost Sheet Lines (Material, Labour and Overheads) -> Allow your purchase, accounting and HR department to select cost center (cost sheet) and cost center line (cost sheet line) to encode for expenses and labour works. -> Create Job Order Issues -> Create Material Requision Request -> Prepare Notes/ToDo lists for Projects and Jobs. ->​
Enabling Job Costing
Creating Cost Centers for Job Costing
project job cost
project job costing
project job contracting
project job contract
job contract
jobs contract
construction
Construction app
Construction odoo
doo Job Costing And Job Cost Sheet (Contracting)
Odoo job cost sheet
job cost sheet odoo
contracting odoo
odoo construction
job costing (Contracting)
odoo job costing (Contracting)
odoo job costing Contracting
job order odoo
work order odoo
job Contracting
job costing
job cost Contracting
Operation cost in batch manufacturing
Operation cost
odoo Contracting
Raw Materials
Contracting odoo job
work in process
    """,
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'http://www.probuse.com',
    'support': 'contact@probuse.com',
    'images': ['static/description/img1.jpg'],
    'live_test_url': 'https://youtu.be/OEmvD09GBLE', #'https://youtu.be/XU_RWJfNlEk',
    'data':[
        'security/ir.model.access.csv',
        'views/mrp_bom_view.xml',
        'views/mrp_job_cost_sheet_view.xml',
        'views/mrp_production_view.xml',
        'views/work_order_view.xml',
        'views/res_config_view.xml',
        'views/company_inherit_views.xml',
        'views/product_templete_inherit.xml',
        'wizard/wizard_costo_ganancia.xml',
        'report/manufacturing_report_view.xml',
        'report/bom_report_view.xml',
        'report/costo_ganancia.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
