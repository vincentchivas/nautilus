# -*-coding: utf-8 -*-
"""
@author: yqyu
@date: 2014-07-15
@description: the filters information of page
"""


list_filters = {
    "name": "status",
    "items": [
        {
            "value": "",
            "display_value": "All",
        },
        {
            "value": "draft",
            "display_value": "Draft",
        },
        {
            "value": "finished",
            "display_value": "Finished",
        }
    ]
}

edit_filters = [
    {
        "name": "status",
        "alias": "Status",
        "values": [
            {
                "value": "",
                "display_value": "All",
            },
            {
                "value": "draft",
                "display_value": "Not Translate",
            },
            {
                "value": "finished",
                "display_value": "Translate",
            }
        ]
    }
]
