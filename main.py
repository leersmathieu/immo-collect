# -*- coding: utf-8 -*-
from class_thread import CustomThread
from function import *

current_search_id = 1  # 0 == appartement / 1 == maison
# min/max pages to process
page_start = 1
page_end = 334  # not included
plage_page = [(1, 2), (2, 3), (3, 4)]
is_firefox = False

thread_list = []
for thread_id in range(0, len(plage_page)):
    t = CustomThread(plage_page[thread_id][0], plage_page[thread_id][1], current_search_id, is_firefox)
    thread_list.append(t)

for t in thread_list:
    t.start()

for t in thread_list:
    t.join()

csv = concat_all_csv("./immo-data/*.csv")
if csv is not None:
    print(csv.describe())
