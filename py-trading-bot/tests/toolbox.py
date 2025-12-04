#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  1 15:16:24 2025

@author: maxime
"""
from general_settings.models import OrderSettings, API, ReportSettings, AlertSettings, SchedulerSettings
from orders.models import IBSettings, Currency


def create_general_settings():
    api1, _=API.objects.get_or_create(name="IB")
    api2, _=API.objects.get_or_create(name="YF")
    
    order_settings, _=OrderSettings.objects.get_or_create(
        default_api_orders=api1,
        default_api_alerting=api1,
        default_api_reporting=api1,
        perform_order=False
        )
    
    c, _=Currency.objects.get_or_create(name="euro",symbol="EUR")
    
    ib_settings, _=IBSettings.objects.get_or_create(
        base_currency=c
        )

    ReportSettings.objects.get_or_create()
    AlertSettings.objects.get_or_create()
    SchedulerSettings.objects.get_or_create()   