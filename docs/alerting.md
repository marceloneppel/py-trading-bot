# Alerting
An automatic alerting via Telegram can be performed by the bot. All stocks that is in your portfolio (PF in admin panel) or in your IB portfolio, will be checked periodically during stock exchange opening time. The settings are defined in the admin panel under Telegram settings.

1. You need a bot in telegram (search on internet, bot_father...). And save its token in trading_bot/etc/TELEGRAM_TOKEN. Think about starting it.
2. Time interval for checking is set by "time interval check", the number is in minutes. Please take into account, that the checking itself takes some time.
3. By default, the algorithm check the change compared to closing price from the day before, like on any portal. The stocks in your portfolios will be checked, not those that are candidates to a strategy. Threshold for alerting is "alert threshold" and alarming is "alarm threshold". They are set in percents.
4. The alerts will recover if the change comes below the threshold "alert hyst". It is an hysteresis to avoid alerting and recovering at high frequency if the price oscillates around the threshold.

The whole alerting mechanism is coded in reporting/telegram.py. The telegram bot is combined with the scheduler and run asynchronous from Django in a Redis server, thanks to Celery.

Note: Indexes for all stock exchanges in the database are checked by default.
Note 2: as of July 2023, the new version of IB mobile app also has alerting functions. You can deactivate this bot alerting by setting high thresholds.

# Source of the data
You can select from why source the data will come. Go in the admin panel under alert settings. There are three categories:
1. Orders: which data source is used to perform the orders.
2. Alerting: : which data source is used for alerting purpose
3. Reporting: which data source is used for creating the report.



