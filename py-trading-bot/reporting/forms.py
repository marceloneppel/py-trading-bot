#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 25 18:57:04 2025

@author: maxime
"""

from django import forms
from orders.models import StockEx, Action, ActionSector, Strategy

class ScanForm(forms.Form):
    list_of_exchanges = forms.ModelMultipleChoiceField(queryset=StockEx.objects.all(),label="List of stock exchanges to be included in the scan")
    list_of_sectors= forms.ModelMultipleChoiceField(queryset=ActionSector.objects.all(), label="List of sectors to be scanned",required=False)
    strategies_to_scan=forms.ModelMultipleChoiceField(queryset=Strategy.objects.all(), label="List of strategies to be scanned")
    period=forms.IntegerField(label="Number of years of the period to download in the past",initial=3)
    restriction=forms.IntegerField(label="(Optional) Reduced the analyzed windows to this number of days",required=False,initial=90)
    fees=forms.FloatField(label="Fees in pu (so 1%=0.01)",initial=0.0)

class DownloadYFForm(forms.Form):
    stock_ex=forms.ModelChoiceField(queryset=StockEx.objects.all(), required=False)
    sector=forms.ModelChoiceField(queryset=ActionSector.objects.all(), required=False)
    actions=forms.ModelMultipleChoiceField(queryset=Action.objects.all(), required=False)
    start=forms.CharField(required=False)
    end=forms.CharField(required=False)
    period=forms.CharField(max_length=100, required=False,initial="3y")
    timeframe=forms.CharField(max_length=100, required=False,initial="1d")
    filename=forms.CharField(max_length=100)
    add_index=forms.BooleanField(initial=True)
    
class DownloadIBForm(forms.Form):
    stock_ex=forms.ModelChoiceField(queryset=StockEx.objects.all(), required=False)
    sector=forms.ModelChoiceField(queryset=ActionSector.objects.all(), required=False)
    actions=forms.ModelMultipleChoiceField(queryset=Action.objects.all(), required=False)
    end=forms.CharField(required=False,initial="")
    period=forms.CharField(max_length=100,initial="3 Y")
    timeframe=forms.CharField(max_length=100, required=False,initial="1 day")
    filename=forms.CharField(max_length=100)
    add_index=forms.BooleanField(initial=True)    
    
    
