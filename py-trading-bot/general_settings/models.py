from django.db import models

class API(models.Model):
    name=models.CharField(max_length=100, blank=False)
    
    def __str__(self):
        return str(self.name)
    
class ReportSettings(models.Model):
    calculate_pattern=models.BooleanField(default=True)
    calculate_trend=models.BooleanField(default=True)
    daily_report_period=models.IntegerField(default=3, verbose_name="Period in years in the past downloaded for the reports")
    
class SchedulerSettings(models.Model):
     pf_check=models.BooleanField(default=True)
     index_check=models.BooleanField(default=True)
     report=models.BooleanField(default=True)
     intraday=models.BooleanField(default=False)
     heartbeat=models.BooleanField(default=False) # to test telegram
     heartbeat_ib=models.BooleanField(default=True) # to test telegram, note ["USED_API_DEFAULT"]["alerting] must be set to IB otherwise, it makes no sense.
     update_slow_strat=models.BooleanField(default=True)  
     time_interval_interday=models.IntegerField(default=60,verbose_name="Time interval for intraday trading, how often should the report runs")
     opening_check_minute_shift=models.IntegerField(default=5,verbose_name="Opening check minute shift, how many minutes after opening should the alerting starts")
     daily_report_minute_shift=models.IntegerField(default=15,verbose_name="Daily report minute shift, how many minutes before closing should the report be generated"    )                            
     
class AlertSettings(models.Model):
     alert_threshold=models.IntegerField(default=3,verbose_name="Alert threshold, in %")  #in %
     alarm_threshold=models.IntegerField(default=5,verbose_name="Alarm threshold, in %")  #in %
     alert_hyst=models.IntegerField(default=1,verbose_name='Alert hysteresis, in %, to avoid alert/recovery cycles')  #in %
                 #margin in % to avoid alert/recovery at high frequency, so if ALERT_THRESHOLD=3 and ALERT_HYST=1
                 #then the alert will be deactivated when the price variation is 2% (3-1)
     time_interval_check=models.IntegerField(default=10,verbose_name="Time interval check for the portfolio price variation, in min")
     time_interval_update=models.IntegerField(default=60,verbose_name="Time interval to update the IB portfolio with the bot, in min")
     
class OrderSettings(models.Model):
     default_api_orders=models.ForeignKey('API',on_delete=models.RESTRICT, related_name="default_api_orders")
     default_api_alerting=models.ForeignKey('API',on_delete=models.RESTRICT, related_name="default_api_alerting")
     default_api_reporting=models.ForeignKey('API',on_delete=models.RESTRICT, related_name="default_api_reporting")
     perform_order=models.BooleanField(default=True)
     
     


