#!/usr/bin/python
# -*- coding: utf-8 -*-

status_map = {
        0: 'New', 1: "Assigned", 2: "In progress", 3: "Pending", 
        4: "Resolved", 5: "Closed", 6: "Canceled"
}
impact_map = {
        1000: '1-Critical', 2000: "2-High", 3000: "3-Medium", 4000: "4-Low"
}
urgency_map = {
        1000: '1-Critical', 2000: "2-High", 3000: "3-Medium", 4000: "4-Low"
}
service_type_map = {
        0: 'User Service Restoration', 1: 'User Service Request', 2: 'Infrastructure Restoration', 3: 'Infrastructure Event'
}
reporter_source_map = {
        1000: "1000", 2000: "2000", 3000: "3000", 4000: "4000", 4200: "4200", 
        5000: "5000", 6000: "6000", 7000: "7000", 8000: "8000", 9000: "9000", 
        10000: "5000", 10000: "5000", 11000: "11000", 12000: "12000"
}
