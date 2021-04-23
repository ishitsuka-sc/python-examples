#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
from texttable import Texttable
 
table = Texttable()
table.set_max_width(0) 
array=[10,20,34,2,2,2,3,3]
table.set_cols_width(array)
table.add_rows([
        ['id', 
            'name',
            'description',
            '11111',
            '222222',
            '333333',
            '4444444',
            '55555'],
        [1, 'aaaaa bbbbb', 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx','1','2','3','4','5'],
        ])
print(table.draw())
