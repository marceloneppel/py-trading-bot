from django.shortcuts import render, redirect
from django.http import HttpResponse
from reporting.telegram import start, cleaning_sub
# Create your views here.
from reporting.models import Report, ActionReport, Alert, OrderExecutionMsg, Scan
from reporting.scanner import Scanner
from orders.models import Action, StockStatus, exchange_to_index_symbol, ActionSector, StockEx, Job,\
                          get_exchange_actions, Strategy, filter_intro_action, ActionCategory
from reporting.forms import ScanForm, DownloadYFForm, DownloadIBForm
from core.data_manager_online import retrieve_data_ib, retrieve_data_notIB

from orders.ib import actualize_ss
from core import caller
from .filter import ReportFilter
from django.utils import timezone
import json

def reportsView(request): 
    reports= Report.objects.all()
    context={'reports': ReportFilter(request.GET, queryset=reports)}
    return render(request, 'reporting/reports.html', context)

def reportView(request,pk):
    report= Report.objects.get(id=pk)
    ars=ActionReport.objects.filter(report=pk)

    context={'report':report, 'ars':ars}
    return render(request, 'reporting/report.html', context)
    
def trendView(request,pk): 
    report= Report.objects.get(id=pk)
    ars=ActionReport.objects.filter(report=pk)
    
    context={'report':report, 'ars':ars}
    return render(request, 'reporting/trend.html', context)

def alertsView(request): 
    alerts= Alert.objects.filter(active=True)
    context={'alerts':alerts}
    return render(request, 'reporting/alerts.html', context)

#manual start to avoid multiple instanciation
def start_bot(request):
    start()
    print("bot_start ok")
    return redirect('reporting:reports')

#For testing purpose
def daily_report_sub(
        exchange:str,
        it_is_index:bool=False,
        **kwargs):
    
    if exchange is not None:
        report1=Report.objects.create(stock_ex=StockEx.objects.get(name=exchange))
    else:
        report1=Report.objects.create()
    report1.daily_report(exchange=exchange,it_is_index=it_is_index,**kwargs)
    
    oems=OrderExecutionMsg.objects.filter(report=report1)
    for oem in oems:
        print(oem.text)
    if report1.text:
        print(report1.text)     

def daily_report(
        request,
        exchange:str,
        **kwargs):
    '''
    Write report for an exchange and/or sector
    Identical to the telegrambot function, but here without bot, so sync instead of async
    Either for test purpose, or if your telegram was stopped
    
    Arguments
   	----------
       request: incoming http request
       exchange: name of the stock exchange
    '''  
    s_ex=StockEx.objects.get(name=exchange)
    a="strategies_in_use"
    print("writting daily report "+s_ex.name)
    if s_ex.presel_at_sector_level:
        for sec in ActionSector.objects.all():
            strats=getattr(sec,a).all()
            if len(strats)!=0: #some strategy is activated for this sector
                print("starting report " + sec.name)
                daily_report_sub(s_ex.name,sec=sec)
    else:
        strats=getattr(s_ex,a).all()
        if len(strats)!=0: 
            daily_report_sub(s_ex.name)

    daily_report_sub(exchange=None,symbols=[exchange_to_index_symbol(s_ex.name)[1]],it_is_index=True)
    return render(request, 'reporting/success_report.html')

def cleaning(request):
    '''
    Deactivate the alert at the end of the day
    '''
    cleaning_sub()
        
    return HttpResponse("cleaning done")

def actualize_ss_view(request):
    actualize_ss()
    return HttpResponse("Stock status actualized")

def create_ss_sub():
    for a in Action.objects.all():
        ss, created=StockStatus.objects.get_or_create(action=a)

def create_ss(request):
    create_ss_sub()
    return HttpResponse("Stock status created")

def trigger_all_jobs(request):
    '''
    If you start with the bot, to create the initial slow presel
    '''
    today=timezone.now()
    for j in Job.objects.all():
        actions=get_exchange_actions(j.stock_ex.name)
        actions=filter_intro_action(actions,j.period_year)
        st=Strategy.objects.get(name=j.strategy.name)
        pr=caller.name_to_ust_or_presel(
            st.class_name, 
            None,
            str(j.period_year)+"y",
            prd=True, 
            actions=actions,
            exchange=j.stock_ex.name,
            st=st
            ) 
        pr.actualize()   
        j.last_execution=today
        j.save()
    return HttpResponse("All jobs ran")

def triggerScanView(request):
    if request.method == "POST":
        form = ScanForm(request.POST)

        if form.is_valid():
            return scan(
                list_of_exchanges=form.cleaned_data["list_of_exchanges"],
                list_of_sectors=form.cleaned_data["list_of_sectors"],
                strategies_to_scan=form.cleaned_data["strategies_to_scan"],
                period=form.cleaned_data["period"],
                restriction=form.cleaned_data["restriction"],
                fees=form.cleaned_data["fees"]
                )
    else:
        form = ScanForm()
    return render(request, "reporting/trigger_scan.html", {"form": form})

def scan(**kwargs):
    '''
    Trigger the scan algorithm
    '''
    s=Scanner(**kwargs)
    res=s.scan_all()

    return HttpResponse("Scan ran successfully " + str(res))

def scansView(request): 
    scans= Scan.objects.all()
    context={'scans': scans}
    return render(request, 'reporting/scans.html', context)

def scanView(request,pk):
    scan=Scan.objects.get(id=pk)
    result_dic=json.loads(scan.results.replace("\'", "\""))
    context={'scan':scan,'result_dic':result_dic}

    return render(request, 'reporting/scan.html', context)


def download_sub(form):
    it_is_index=False
    
    actions=form.cleaned_data["actions"]

    if actions is None or len(actions)==0:
        if form.cleaned_data["sector"] is None:
            sec=None
        else:
            sec=form.cleaned_data["sector"].name
        
        actions=get_exchange_actions(form.cleaned_data["stock_ex"].name,sec=sec) 
    else:
        it_is_index=True
        cat=ActionCategory.objects.get(short="IND")
        for a in actions:    
            if a.category!=cat:
                it_is_index=False
                break
    return actions, it_is_index
                                      
def download_yf(request):
    if request.method == "POST":
        form = DownloadYFForm(request.POST)
        
        if form.is_valid():
            actions, it_is_index=download_sub(form)

            arr=retrieve_data_notIB(
                "YF",
                actions,
                form.cleaned_data["period"],
                it_is_index=it_is_index,
                start=form.cleaned_data["start"],
                end=form.cleaned_data["end"],
                timeframe=form.cleaned_data["timeframe"],
                save=True,
                filename=form.cleaned_data["filename"],
                add_index=form.cleaned_data["add_index"],
                )
            if arr is None:
                return HttpResponse("Download with YF failed")
            else:
                return HttpResponse("Download with YF successful")
        else:
            return HttpResponse("Form is not valid")            
    else:
        form = DownloadYFForm()
        return render(request, "reporting/download_yf.html", {"form": form})        

def download_ib(request):
    if request.method == "POST":
        form = DownloadIBForm(request.POST)

        if form.is_valid():
            actions, it_is_index=download_sub(form)

            if form.cleaned_data["end"] is None:
                end="" #default value for IB
            else:
                end=form.cleaned_data["end"]

            arr=retrieve_data_ib(
                actions,
                form.cleaned_data["period"],
                it_is_index=it_is_index,
                end=end,
                timeframe=form.cleaned_data["timeframe"],
                bypass_conversion=True,
                save=True,
                filename=form.cleaned_data["filename"],
                add_index=form.cleaned_data["add_index"]
                )
            if arr is None:
                return HttpResponse("Download with IB failed")
            else:
                return HttpResponse("Download with IB successful")
        else:
            return HttpResponse("Form is not valid")
    else:
        form = DownloadIBForm()
        return render(request, "reporting/download_ib.html", {"form": form})    

def test_order(request):
    symbol=""
    strategy=""
    exchange="XETRA"
    short=False
    return render(request, 'reporting/success_report.html')
    #with MyIB() as myIB:
    #    return myIB.entry_order(symbol,strategy, exchange,short), True
    
    return HttpResponse("test")

def test(request):
    from ib_insync import Stock
    import vectorbtpro as vbt
        
    import logging
    from orders.ib import place
    #logger = logging.getLogger(__name__)
    action=Action.objects.get(symbol="IBM")
    txt, _, _= place(True,
                            action,
                            False,
                            order_size=15000)
    #action=Action.objects.get(symbol="EN.PA")
    #myIB=MyIB()
    
    #contract = Stock(action.ib_ticker,action.stock_ex.ib_ticker, action.currency.symbol)
    #myIB.get_past_closing_price(contract)
    #cours_open, cours_close, cours_low, cours_high=retrieve_data(["EN.PA","DG.PA"],"1y")
    #macd=vbt.MACD.run(cours_close)
    #print(macd.macd)
    #print(myIB.positions())
    
    
    #check_hold_duration("KER.PA",False,key="retard")
    #report=Report(ent_symbols=[],ex_symbols=[])
    #report.save()
    #report.daily_report_17h()
    
    #
    #myIB.test("OR.PA")
    #myIB.entry_order("OR.PA",False,strat19=True)
    #myIB.exit_order("OR.PA",False,strat19=True)
    #print(myIB.ib.accountSummary())
    #print(myIB.ib.accountValues())
    #print(myIB.ib.positions())

    #retrieve('AAPL',"10 D")    
    #myIB.disconnect()
    
    return HttpResponse("test ok")