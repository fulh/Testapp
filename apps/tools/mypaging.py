#!/usr/bin/evn python
# -*-coding:utf-8 -*-
__author__ = "FuLiHua"

class Page():
    def __init__(self,action_page,counter,per_max_page,url,per_page=10):
        self.action_page = action_page
        self.counter = counter
        self.per_page = per_page
        self.per_max_page = per_max_page
        self.url = url

        counter_page, m = divmod(self.counter, self.per_page)

        if m:
            counter_page = counter_page + 1
        if self.action_page > counter_page:
            self.action_page = counter_page
        if counter_page < self.per_max_page:
            self.per_max_page = counter_page

        half_page = self.per_max_page // 2
        start_page = self.action_page - half_page
        end_page = self.action_page + half_page
        if start_page <= 1:
            start_page = 1
            end_page = self.per_max_page
        if end_page >= counter_page:
            start_page = counter_page - self.per_max_page + 1
            end_page = counter_page
        self.counter_page = counter_page
        self.start_page = start_page
        self.end_page = end_page

        start_number = (self.action_page - 1) * per_page
        end_number = self.action_page * per_page
        if start_number < 0:
            start_number = 0
        if end_number <= 0:
            end_number = counter
        self.start_number=start_number
        self.end_number = end_number

    @property
    def start(self):
        return self.start_number

    @property
    def end(self):
        return self.end_number


    def html(self):
        list_html_str = []
        if self.action_page <= 1:
            list_html_str.append(
                '<li class="page-item disabled"><a class="page-link" aria-label="Previous"><span aria-hidden="true">&laquo;</span></a></li>')
        else:
            list_html_str.append(
                '<li class="page-item" ><a class="page-link" href="{0}-{1}" aria-label="Previous"><span aria-hidden="true">&laquo;</span></a></li>'.format(self.url,self.action_page-1))

        for i in range(self.start_page, self.end_page + 1):
            if self.action_page == i:
                list_html_str.append('<li class="page-item active" aria-current="page"><span class="page-link">{}</span></li>'.format(i))
            else:
                list_html_str.append('<li class="page-item"><a class="page-link" href="{0}-{1}">{1}</a></li>'.format(self.url, i))

        if self.action_page >= self.counter_page:
            list_html_str.append(
                '<li class="page-item disabled"><a class="page-link" aria-label="Next"><span aria-hidden="true">&raquo;</span></a></li>')
        else:
            list_html_str.append(
                '<li class="page-item" ><a class="page-link" href="{0}-{1}" aria-label="Next"><span aria-hidden="true">&raquo;</span></a></li>'.format(self.url,self.action_page+1))

        return "".join(list_html_str)
