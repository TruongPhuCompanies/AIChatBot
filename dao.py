from datetime import datetime, timedelta

def get_revenue_by_date_range(orders, start_date, end_date):
    if isinstance(start_date, str):
        start_date = datetime.fromisoformat(start_date)
 
    if isinstance(end_date, str):
        end_date = datetime.fromisoformat(end_date)

    total = 0.0
    for order in orders:
        order_date = order['date_order']
        
        if isinstance(order_date, datetime):
            order_date = order_date.replace(tzinfo=None)
        else:
            order_date = datetime.fromisoformat(order_date)

        if start_date <= order_date <= end_date:
            total += order['amount_total']
    
    return total


def get_last_week_revenue(orders):
    today = datetime.today()
    start_date = today - timedelta(days=today.weekday() + 7)
    end_date = start_date + timedelta(days=6)
    return get_revenue_by_date_range(orders, start_date, end_date)

def get_this_month_revenue(orders):
    today = datetime.today()
    start_date = today.replace(day=1)
    end_date = today.replace(day=1, month=today.month + 1) - timedelta(days=1)
    return get_revenue_by_date_range(orders, start_date, end_date)
