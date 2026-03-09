from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count, Avg
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
import csv
import json
from decimal import Decimal
from datetime import datetime
import io
import calendar
import uuid
from .models import Achievement, Trade, Event
from .forms import AchievementForm, EventForm, TradeForm, TradeFilterForm, CSVUploadForm

@login_required
def dashboard(request):
    # Check if this is an AJAX request for calendar data
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return get_calendar_data(request)
    
    user_trades = Trade.objects.filter(user=request.user)
    
    # Calculate statistics
    total_trades = user_trades.count()
    completed_trades = user_trades.exclude(exit_price__isnull=True)
    
    if completed_trades.exists():
        # Calculate actual winning trades based on profit_loss
        winning_trades = 0
        total_pl = Decimal('0')
        
        for trade in completed_trades:
            if trade.profit_loss and trade.profit_loss > 0:
                winning_trades += 1
            if trade.profit_loss:
                total_pl += trade.profit_loss
        
        win_rate = (winning_trades / completed_trades.count()) * 100 if completed_trades.count() > 0 else 0
        
        # Best and worst trades
        best_trade = max(completed_trades, key=lambda t: t.profit_loss or 0, default=None)
        worst_trade = min(completed_trades, key=lambda t: t.profit_loss or 0, default=None)
        
        # Average risk:reward
        rr_trades = [trade for trade in completed_trades if trade.risk_reward_ratio]
        avg_rr = sum([trade.risk_reward_ratio for trade in rr_trades]) / len(rr_trades) if rr_trades else 0
    else:
        win_rate = 0
        total_pl = Decimal('0')
        best_trade = None
        worst_trade = None
        avg_rr = 0
    
    # Monthly and weekly data for charts
    now = timezone.now()
    monthly_data = []
    weekly_data = []
    monthly_pl_data = []
    
    # Monthly data
    for i in range(12):
        month_start = (now - timedelta(days=30*i)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        month_trades = user_trades.filter(open_date__range=[month_start, month_end])
        count = month_trades.count()
        month_pl = sum([trade.profit_loss for trade in month_trades if trade.profit_loss]) or 0
        monthly_data.append({
            'month': month_start.strftime('%b %Y'),
            'count': count,
            'pl': float(month_pl)
        })
        monthly_pl_data.append(float(month_pl))
    
    monthly_data.reverse()
    monthly_pl_data.reverse()
    
    # Weekly data
    for i in range(12):
        week_start = now - timedelta(weeks=i+1)
        week_end = now - timedelta(weeks=i)
        week_trades = user_trades.filter(open_date__range=[week_start, week_end])
        count = week_trades.count()
        weekly_data.append({
            'week': f'Week {i+1}',
            'count': count
        })
    
    weekly_data.reverse()
    
    # Calendar data for current month
    # Get month/year from request parameters or use current
    current_year = int(request.GET.get('year', now.year))
    current_month = int(request.GET.get('month', now.month))
    
    # Calculate previous and next month/year
    if current_month == 1:
        prev_month = 12
        prev_year = current_year - 1
    else:
        prev_month = current_month - 1
        prev_year = current_year
    
    if current_month == 12:
        next_month = 1
        next_year = current_year + 1
    else:
        next_month = current_month + 1
        next_year = current_year
    
    year = current_year
    month = current_month
    
    # Get trades for the month
    month_start = datetime(year, month, 1)
    if month == 12:
        month_end = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        month_end = datetime(year, month + 1, 1) - timedelta(days=1)
    
    month_trades = user_trades.filter(
        open_date__range=[month_start, month_end]
    ).order_by('open_date')
    
    # Calculate monthly statistics
    month_total_trades = month_trades.count()
    month_pl = sum([trade.profit_loss for trade in month_trades if trade.profit_loss]) or 0
    month_winning_trades = sum(1 for trade in month_trades if trade.profit_loss and trade.profit_loss > 0)
    month_win_rate = (month_winning_trades / month_total_trades * 100) if month_total_trades > 0 else 0
    
    # Calculate weekly statistics for current month
    weeks_in_month = []
    current_date = month_start
    week_num = 1
    
    while current_date <= month_end:
        week_start = current_date
        week_end = min(current_date + timedelta(days=6), month_end)
        
        week_trades = month_trades.filter(open_date__date__range=[week_start.date(), week_end.date()])
        week_pl = sum([trade.profit_loss for trade in week_trades if trade.profit_loss]) or 0
        
        weeks_in_month.append({
            'week_num': week_num,
            'start_date': week_start,
            'end_date': week_end,
            'trades_count': week_trades.count(),
            'pl': float(week_pl)
        })
        
        current_date += timedelta(days=7)
        week_num += 1
    
    # Create calendar data
    cal = calendar.monthcalendar(year, month)
    calendar_data = []
    
    for week in cal:
        week_data = []
        for day in week:
            if day == 0:
                week_data.append({'day': 0, 'trades': []})
            else:
                day_trades = month_trades.filter(open_date__day=day)
                # Convert trades to serializable format
                trades_data = []
                for trade in day_trades:
                    trades_data.append({
                        'id': trade.id,
                        'asset': trade.asset,
                        'trade_type': trade.trade_type,
                        'profit_loss': float(trade.profit_loss) if trade.profit_loss else 0,
                        'entry_price': float(trade.entry_price),
                        'exit_price': float(trade.exit_price) if trade.exit_price else None,
                    })
                
                week_data.append({
                    'day': day,
                    'trades': trades_data,
                    'profit': sum([t.profit_loss for t in day_trades if t.profit_loss]) or 0
                })
        calendar_data.append(week_data)
    # Get latest events and achievements
    latest_events = Event.objects.filter(user=request.user).order_by('-event_date')[:5]
    latest_achievements = Achievement.objects.filter(user=request.user).order_by('-achieved_date')[:5]
    
    # Get upcoming events (next 5 upcoming events)
    upcoming_events = Event.objects.filter(
        user=request.user, 
        event_date__gte=now,
        is_completed=False
    ).order_by('event_date')[:5]
    
    # Get recent achievements (last 30 days)
    thirty_days_ago = now - timedelta(days=30)
    recent_achievements = Achievement.objects.filter(
        user=request.user,
        achieved_date__gte=thirty_days_ago
    ).order_by('-achieved_date')[:3]

    context = {
        'total_trades': total_trades,
        'win_rate': round(win_rate, 2),
        'total_pl': float(total_pl),
        'best_trade': best_trade,
        'worst_trade': worst_trade,
        'avg_rr': round(avg_rr, 2),
        'monthly_data': json.dumps(monthly_data),
        'weekly_data': json.dumps(weekly_data),
        'monthly_pl_data': json.dumps(monthly_pl_data),
        'recent_trades': user_trades[:5],
        'calendar_data': calendar_data,
        'current_month': calendar.month_name[month],
        'current_year': year,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
        'month_total_trades': month_total_trades,
        'month_pl': float(month_pl),
        'month_win_rate': round(month_win_rate, 2),
        'weeks_in_month': weeks_in_month,
        'latest_events': latest_events,
        'latest_achievements': latest_achievements,
    }
    
    return render(request, 'trades/dashboard.html', context)

@login_required
def get_calendar_data(request):
    """AJAX endpoint for calendar data"""
    user_trades = Trade.objects.filter(user=request.user)
    now = timezone.now()

    # Get month/year from request parameters or use current
    current_year = int(request.GET.get('year', now.year))
    current_month = int(request.GET.get('month', now.month))

    # Calculate previous and next month/year
    if current_month == 1:
        prev_month, prev_year = 12, current_year - 1
    else:
        prev_month, prev_year = current_month - 1, current_year

    if current_month == 12:
        next_month, next_year = 1, current_year + 1
    else:
        next_month, next_year = current_month + 1, current_year

    # Month start and end
    month_start = datetime(current_year, current_month, 1)
    if current_month == 12:
        month_end = datetime(current_year + 1, 1, 1) - timedelta(days=1)
    else:
        month_end = datetime(current_year, current_month + 1, 1) - timedelta(days=1)

    month_trades = user_trades.filter(
        open_date__range=[month_start, month_end]
    ).order_by('open_date')

    # Monthly stats
    month_total_trades = month_trades.count()
    month_pl = sum([trade.profit_loss for trade in month_trades if trade.profit_loss]) or 0
    month_winning_trades = sum(1 for trade in month_trades if trade.profit_loss and trade.profit_loss > 0)
    month_win_rate = (month_winning_trades / month_total_trades * 100) if month_total_trades > 0 else 0

    # Weekly stats
    weeks_in_month = []
    current_date = month_start
    week_num = 1

    while current_date <= month_end:
        week_start = current_date
        week_end = min(current_date + timedelta(days=6), month_end)
        week_trades = month_trades.filter(open_date__date__range=[week_start.date(), week_end.date()])
        week_pl = sum([trade.profit_loss for trade in week_trades if trade.profit_loss]) or 0

        weeks_in_month.append({
            'week_num': week_num,
            'start_date': week_start.strftime("%Y-%m-%d"),
            'end_date': week_end.strftime("%Y-%m-%d"),
            'trades_count': week_trades.count(),
            'pl': float(week_pl)
        })

        current_date += timedelta(days=7)
        week_num += 1

    # Calendar data (JSON serializable)
    cal = calendar.monthcalendar(current_year, current_month)
    calendar_data = []

    for week in cal:
        week_data = []
        for day in week:
            if day == 0:
                week_data.append({'day': 0, 'trades': []})
            else:
                day_trades = month_trades.filter(open_date__day=day)
                week_data.append({
                    'day': day,
                    'trades': [
                        {
                            "id": t.id,
                            "symbol": t.symbol,
                            "open_date": t.open_date.strftime("%Y-%m-%d %H:%M:%S"),
                            "profit_loss": float(t.profit_loss) if t.profit_loss else 0
                        }
                        for t in day_trades
                    ],
                    'profit': sum([t.profit_loss for t in day_trades if t.profit_loss]) or 0
                })
        calendar_data.append(week_data)

    # Final JSON-safe context
    context = {
        'calendar_data': calendar_data,
        'current_month': calendar.month_name[current_month],
        'current_year': current_year,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
        'month_total_trades': month_total_trades,
        'month_pl': float(month_pl),
        'month_win_rate': round(month_win_rate, 2),
        'weeks_in_month': weeks_in_month,
    }

    return JsonResponse(context, safe=False)
@login_required
def trade_list(request):
    trades = Trade.objects.filter(user=request.user)
    form = TradeFilterForm(request.GET)
    
    if form.is_valid():
        if form.cleaned_data['asset']:
            trades = trades.filter(asset__icontains=form.cleaned_data['asset'])
        if form.cleaned_data['trade_type']:
            trades = trades.filter(trade_type=form.cleaned_data['trade_type'])
        if form.cleaned_data['date_from']:
            trades = trades.filter(open_date__date__gte=form.cleaned_data['date_from'])
        if form.cleaned_data['date_to']:
            trades = trades.filter(open_date__date__lte=form.cleaned_data['date_to'])
        if form.cleaned_data['tags']:
            trades = trades.filter(tags__icontains=form.cleaned_data['tags'])
    
    paginator = Paginator(trades, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'trades/trade_list.html', {
        'page_obj': page_obj,
        'form': form,
    })

@login_required
def merge_trades(request):
    if request.method == 'POST':
        trade_ids = request.POST.getlist('trade_ids')
        
        if len(trade_ids) < 2:
            messages.error(request, 'Please select at least 2 trades to merge.')
            return redirect('trade_list')
        
        trades = Trade.objects.filter(id__in=trade_ids, user=request.user)
        
        # Validate that all trades can be merged
        first_trade = trades.first()
        for trade in trades:
            if not first_trade.can_merge_with(trade) and trade != first_trade:
                messages.error(request, f'Cannot merge trades with different symbols or types.')
                return redirect('trade_list')
        
        # Create merged trade
        merged_group_id = str(uuid.uuid4())
        
        # Store original trades data
        original_trades_data = []
        for trade in trades:
            original_trades_data.append({
                'id': trade.id,
                'open_date': trade.open_date.isoformat(),
                'close_date': trade.close_date.isoformat() if trade.close_date else None,
                'entry_price': str(trade.entry_price),
                'exit_price': str(trade.exit_price) if trade.exit_price else None,
                'position_size': str(trade.position_size),
                'commission': str(trade.commission),
                'swap': str(trade.swap),
                'profit': str(trade.profit) if trade.profit else None,
                'tags': trade.tags,
                'notes': trade.notes,
            })
        
        # Calculate merged values
        total_position_size = sum([trade.position_size for trade in trades])
        total_commission = sum([trade.commission for trade in trades])
        total_swap = sum([trade.swap for trade in trades])
        total_profit = sum([trade.profit or 0 for trade in trades])
        
        # Calculate weighted average entry price
        weighted_entry = sum([trade.entry_price * trade.position_size for trade in trades]) / total_position_size
        
        # Calculate weighted average exit price (if all trades are closed)
        closed_trades = [t for t in trades if t.exit_price]
        weighted_exit = None
        if len(closed_trades) == len(trades):
            weighted_exit = sum([trade.exit_price * trade.position_size for trade in closed_trades]) / total_position_size
        
        # Use the first trade as the base for merged trade
        merged_trade = trades.first()
        merged_trade.position_size = total_position_size
        merged_trade.entry_price = weighted_entry
        merged_trade.exit_price = weighted_exit
        merged_trade.commission = total_commission
        merged_trade.swap = total_swap
        merged_trade.profit = total_profit
        merged_trade.is_merged = True
        merged_trade.merged_group_id = merged_group_id
        merged_trade.merged_trades_count = len(trades)
        merged_trade.original_trades_data = original_trades_data
        merged_trade.tags = f"merged,{merged_trade.tags}" if merged_trade.tags else "merged"
        merged_trade.save()
        
        # Delete other trades
        trades.exclude(id=merged_trade.id).delete()
        
        messages.success(request, f'Successfully merged {len(trades)} trades.')
        return redirect('trade_detail', pk=merged_trade.pk)
    
    return redirect('trade_list')

@login_required
def unmerge_trade(request, pk):
    trade = get_object_or_404(Trade, pk=pk, user=request.user)
    
    if not trade.is_merged or not trade.original_trades_data:
        messages.error(request, 'This trade cannot be unmerged.')
        return redirect('trade_detail', pk=pk)
    
    if request.method == 'POST':
        # Recreate original trades
        for trade_data in trade.original_trades_data:
            Trade.objects.create(
                user=request.user,
                open_date=datetime.fromisoformat(trade_data['open_date'].replace('Z', '+00:00')),
                close_date=datetime.fromisoformat(trade_data['close_date'].replace('Z', '+00:00')) if trade_data['close_date'] else None,
                asset=trade.asset,
                trade_type=trade.trade_type,
                entry_price=Decimal(trade_data['entry_price']),
                exit_price=Decimal(trade_data['exit_price']) if trade_data['exit_price'] else None,
                position_size=Decimal(trade_data['position_size']),
                commission=Decimal(trade_data['commission']),
                swap=Decimal(trade_data['swap']),
                profit=Decimal(trade_data['profit']) if trade_data['profit'] else None,
                tags=trade_data['tags'],
                notes=trade_data['notes'],
                stop_loss=trade.stop_loss,
                take_profit=trade.take_profit,
                emotion=trade.emotion,
            )
        
        # Delete merged trade
        trade.delete()
        
        messages.success(request, f'Successfully unmerged trade into {len(trade.original_trades_data)} original trades.')
        return redirect('trade_list')
    
    return render(request, 'trades/unmerge_confirm.html', {'trade': trade})
@login_required
def trade_detail(request, pk):
    trade = get_object_or_404(Trade, pk=pk, user=request.user)
    return render(request, 'trades/trade_detail.html', {'trade': trade})

@login_required
def trade_create(request):
    if request.method == 'POST':
        form = TradeForm(request.POST, request.FILES)
        if form.is_valid():
            trade = form.save(commit=False)
            trade.user = request.user
            trade.save()
            messages.success(request, 'Trade added successfully!')
            return redirect('trade_detail', pk=trade.pk)
    else:
        form = TradeForm()
    
    return render(request, 'trades/trade_form.html', {'form': form, 'title': 'Add New Trade'})

@login_required
def trade_update(request, pk):
    trade = get_object_or_404(Trade, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = TradeForm(request.POST, request.FILES, instance=trade)
        if form.is_valid():
            form.save()
            messages.success(request, 'Trade updated successfully!')
            return redirect('trade_detail', pk=trade.pk)
    else:
        form = TradeForm(instance=trade)
    
    return render(request, 'trades/trade_form.html', {
        'form': form, 
        'title': 'Edit Trade',
        'trade': trade
    })

@login_required
def trade_delete(request, pk):
    trade = get_object_or_404(Trade, pk=pk, user=request.user)
    
    if request.method == 'POST':
        trade.delete()
        messages.success(request, 'Trade deleted successfully!')
        return redirect('trade_list')
    
    return render(request, 'trades/trade_confirm_delete.html', {'trade': trade})

@login_required
def export_trades_csv(request):
    trades = Trade.objects.filter(user=request.user)
    
    # Apply filters if provided
    form = TradeFilterForm(request.GET)
    if form.is_valid():
        if form.cleaned_data['asset']:
            trades = trades.filter(asset__icontains=form.cleaned_data['asset'])
        if form.cleaned_data['trade_type']:
            trades = trades.filter(trade_type=form.cleaned_data['trade_type'])
        if form.cleaned_data['date_from']:
            trades = trades.filter(open_date__date__gte=form.cleaned_data['date_from'])
        if form.cleaned_data['date_to']:
            trades = trades.filter(open_date__date__lte=form.cleaned_data['date_to'])
        if form.cleaned_data['tags']:
            trades = trades.filter(tags__icontains=form.cleaned_data['tags'])
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="trades_{timezone.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Open Date', 'Close Date', 'Asset', 'Type', 'Entry Price', 'Exit Price', 'Position Size',
        'Stop Loss', 'Take Profit', 'Commission', 'Swap', 'P&L', 'Tags', 'Notes', 'Emotion'
    ])
    
    for trade in trades:
        writer.writerow([
            trade.open_date.strftime('%Y-%m-%d %H:%M'),
            trade.close_date.strftime('%Y-%m-%d %H:%M') if trade.close_date else '',
            trade.asset,
            trade.trade_type,
            trade.entry_price,
            trade.exit_price or '',
            trade.position_size,
            trade.stop_loss or '',
            trade.take_profit or '',
            trade.commission,
            trade.swap,
            trade.profit_loss or '',
            trade.tags,
            trade.notes,
            trade.emotion,
        ])
    
    return response

@login_required
def import_trades_csv(request):
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            
            try:
                # Read CSV file
                decoded_file = csv_file.read().decode('utf-8')
                csv_data = csv.DictReader(io.StringIO(decoded_file))
                
                imported_count = 0
                errors = []
                
                for row_num, row in enumerate(csv_data, start=2):  # Start at 2 because row 1 is header
                    try:
                        # Parse the CSV data based on your format
                        symbol = row.get('Symbol', '').strip()
                        trade_type = row.get('Type', '').strip().upper()
                        
                        # Parse dates
                        open_date_str = row.get('Open Date', '').strip()
                        closed_date_str = row.get('Closed Date', '').strip()
                        
                        # Parse prices
                        open_price = float(row.get('Open', 0))
                        closed_price_str = row.get('Closed', '').strip()
                        closed_price = float(closed_price_str) if closed_price_str else None
                        
                        # Parse other fields
                        tp_str = row.get('TP', '').strip()
                        sl_str = row.get('SL', '').strip()
                        lots = float(row.get('Lots', 0))
                        profit_str = row.get('Profit', '').strip()
                        commission_str = row.get('Commission', '').strip()

                        # Skip empty rows
                        if not symbol or not trade_type or not open_price:
                            continue
                        
                        # Parse dates with multiple formats
                        date_formats = [
                            '%b %d, %Y %I:%M %p',  # Jul 22, 2025 2:50 PM
                            '%b %d, %Y %I:%M:%S %p',  # Jul 22, 2025 2:50:30 PM
                            '%m/%d/%Y %H:%M',  # 07/22/2025 14:50
                            '%Y-%m-%d %H:%M:%S',  # 2025-07-22 14:50:00
                        ]
                        
                        entry_datetime = None
                        for date_format in date_formats:
                            try:
                                entry_datetime = datetime.strptime(open_date_str, date_format)
                                break
                            except ValueError:
                                continue
                        
                        if not entry_datetime:
                            errors.append(f'Row {row_num}: Invalid date format for Open Date: {open_date_str}')
                            continue
                        
                        # Parse take profit and stop loss
                        take_profit = float(tp_str) if tp_str and tp_str != '' else None
                        stop_loss = float(sl_str) if sl_str and sl_str != '' else None
                        
                        # Parse profit (remove currency symbols and convert)
                        profit = None
                        if profit_str:
                            # Remove currency symbols and convert to float
                            profit_clean = profit_str.replace('$', '').replace('+', '').replace(',', '')
                            try:
                                profit = float(profit_clean)
                            except ValueError:
                                pass
                                                # Parse close date (if provided)
                        close_datetime = None
                        if closed_date_str:
                            for date_format in date_formats:
                                try:
                                    close_datetime = datetime.strptime(closed_date_str, date_format)
                                    break
                                except ValueError:
                                    continue
                            
                            if not close_datetime:
                                errors.append(f'Row {row_num}: Invalid date format for Closed Date: {closed_date_str}')
                                continue
                        # Parse commission
                        commission = 0
                        if commission_str:
                            # Remove currency symbols and convert to float
                            commission_clean = commission_str.replace('$', '').replace('+', '').replace('-', '').replace(',', '')
                            try:
                                commission = float(commission_clean)
                            except ValueError:
                                commission = 0

                        # Create the trade
                        trade = Trade(
                            user=request.user,
                            open_date=entry_datetime,
                            close_date=close_datetime,
                            asset=symbol,
                            trade_type='BUY' if trade_type == 'BUY' else 'SELL',
                            entry_price=Decimal(str(open_price)),
                            exit_price=Decimal(str(closed_price)) if closed_price else None,
                            position_size=Decimal(str(lots)),
                            stop_loss=Decimal(str(stop_loss)) if stop_loss else None,
                            take_profit=Decimal(str(take_profit)) if take_profit else None,
                            commission=Decimal(str(commission)),
                            profit=Decimal(str(profit)) if profit is not None else None,
                            tags='imported',
                            notes=f'Imported from CSV. Original profit: {profit_str}' if profit_str else 'Imported from CSV'
                        )
                        
                        trade.save()
                        imported_count += 1
                        
                    except Exception as e:
                        errors.append(f'Row {row_num}: {str(e)}')
                        continue
                
                # Show results
                if imported_count > 0:
                    messages.success(request, f'Successfully imported {imported_count} trades!')
                
                if errors:
                    error_msg = f'Encountered {len(errors)} errors during import. First few errors: ' + '; '.join(errors[:3])
                    messages.warning(request, error_msg)
                
                if imported_count == 0 and not errors:
                    messages.info(request, 'No valid trades found in the CSV file.')
                
                return redirect('trade_list')
                
            except Exception as e:
                messages.error(request, f'Error processing CSV file: {str(e)}')
    else:
        form = CSVUploadForm()
    
    return render(request, 'trades/import_csv.html', {'form': form})

@login_required
def events_list(request):
    events = Event.objects.filter(user=request.user)
    return render(request, 'trades/events_list.html', {'events': events})

@login_required
def event_create(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.user = request.user
            event.save()
            messages.success(request, 'Event created successfully!')
            return redirect('events_list')
    else:
        form = EventForm()
    return render(request, 'trades/event_form.html', {'form': form, 'title': 'Add Event'})

@login_required
def event_update(request, pk):
    event = get_object_or_404(Event, pk=pk, user=request.user)
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event updated successfully!')
            return redirect('events_list')
    else:
        form = EventForm(instance=event)
    return render(request, 'trades/event_form.html', {'form': form, 'title': 'Edit Event', 'event': event})

@login_required
def event_delete(request, pk):
    event = get_object_or_404(Event, pk=pk, user=request.user)
    if request.method == 'POST':
        event.delete()
        messages.success(request, 'Event deleted successfully!')
        return redirect('events_list')
    return render(request, 'trades/event_confirm_delete.html', {'event': event})

@login_required
def achievements_list(request):
    achievements = Achievement.objects.filter(user=request.user)
    return render(request, 'trades/achievements_list.html', {'achievements': achievements})

@login_required
def achievement_create(request):
    if request.method == 'POST':
        form = AchievementForm(request.POST, request.FILES)
        if form.is_valid():
            achievement = form.save(commit=False)
            achievement.user = request.user
            achievement.save()
            messages.success(request, 'Achievement created successfully!')
            return redirect('achievements_list')
    else:
        form = AchievementForm()
    return render(request, 'trades/achievement_form.html', {'form': form, 'title': 'Add Achievement'})

@login_required
def achievement_update(request, pk):
    achievement = get_object_or_404(Achievement, pk=pk, user=request.user)
    if request.method == 'POST':
        form = AchievementForm(request.POST, request.FILES, instance=achievement)
        if form.is_valid():
            form.save()
            messages.success(request, 'Achievement updated successfully!')
            return redirect('achievements_list')
    else:
        form = AchievementForm(instance=achievement)
    return render(request, 'trades/achievement_form.html', {'form': form, 'title': 'Edit Achievement', 'achievement': achievement})

@login_required
def achievement_delete(request, pk):
    achievement = get_object_or_404(Achievement, pk=pk, user=request.user)
    if request.method == 'POST':
        achievement.delete()
        messages.success(request, 'Achievement deleted successfully!')
        return redirect('achievements_list')
    return render(request, 'trades/achievement_confirm_delete.html', {'achievement': achievement})