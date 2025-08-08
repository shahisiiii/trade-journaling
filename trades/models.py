from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal

User = get_user_model()

# Forex pairs with their flag images
FOREX_PAIRS = [
    ('EURUSD', 'EUR/USD',),
    ('GBPUSD', 'GBP/USD',),
    ('USDJPY', 'USD/JPY',),
    ('USDCHF', 'USD/CHF',),
    ('AUDUSD', 'AUD/USD',),
    ('USDCAD', 'USD/CAD', ),
    ('NZDUSD', 'NZD/USD', ),
    ('EURGBP', 'EUR/GBP', ),
    ('EURJPY', 'EUR/JPY', ),
    ('GBPJPY', 'GBP/JPY', ),
    ('XAUUSD', 'XAU/USD (Gold)',),
    ('XAGUSD', 'XAG/USD (Silver)',),
    ('BTCUSD', 'BTC/USD', ),
    ('ETHUSD', 'ETH/USD', ),
]

class Event(models.Model):
    EVENT_TYPES = [
        ('ECONOMIC', 'Economic Event'),
        ('EARNINGS', 'Earnings Report'),
        ('NEWS', 'Market News'),
        ('PERSONAL', 'Personal Event'),
        ('WEBINAR', 'Webinar/Education'),
        ('OTHER', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, default='OTHER')
    event_date = models.DateTimeField()
    image = models.ImageField(upload_to='events/', null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-event_date']
    
    def __str__(self):
        return f"{self.title} - {self.event_date.strftime('%Y-%m-%d')}"
    
    @property
    def is_upcoming(self):
        return self.event_date > timezone.now() and not self.is_completed

class Achievement(models.Model):
    ACHIEVEMENT_TYPES = [
        ('MILESTONE', 'Trading Milestone'),
        ('PROFIT', 'Profit Target'),
        ('STREAK', 'Winning Streak'),
        ('EDUCATION', 'Education/Certification'),
        ('PERSONAL', 'Personal Goal'),
        ('OTHER', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    achievement_type = models.CharField(max_length=20, choices=ACHIEVEMENT_TYPES, default='OTHER')
    achieved_date = models.DateTimeField(default=timezone.now)
    image = models.ImageField(upload_to='achievements/', null=True, blank=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-achieved_date']
    
    def __str__(self):
        return f"{self.title} - {self.achieved_date.strftime('%Y-%m-%d')}"
class Trade(models.Model):
    TRADE_TYPES = [
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
    ]
    
    EMOTIONS = [
        ('CALM', 'Calm'),
        ('ANXIOUS', 'Anxious'),
        ('GREEDY', 'Greedy'),
        ('FEARFUL', 'Fearful'),
        ('CONFIDENT', 'Confident'),
        ('EXCITED', 'Excited'),
        ('FRUSTRATED', 'Frustrated'),
        ('DISCIPLINED', 'Disciplined'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trades')
    open_date = models.DateTimeField(default=timezone.now)
    close_date = models.DateTimeField(null=True, blank=True)
    asset = models.CharField(max_length=20, choices=FOREX_PAIRS)
    trade_type = models.CharField(max_length=4, choices=TRADE_TYPES)
    entry_price = models.DecimalField(max_digits=12, decimal_places=5)
    exit_price = models.DecimalField(max_digits=12, decimal_places=5, null=True, blank=True)
    position_size = models.DecimalField(max_digits=12, decimal_places=2)
    stop_loss = models.DecimalField(max_digits=12, decimal_places=5, null=True, blank=True)
    take_profit = models.DecimalField(max_digits=12, decimal_places=5, null=True, blank=True)
    commission = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    swap = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    profit = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    tags = models.CharField(max_length=200, blank=True, help_text="Comma-separated tags")
    screenshot = models.ImageField(upload_to='trade_screenshots/', null=True, blank=True)
    notes = models.TextField(blank=True)
    emotion = models.CharField(max_length=20, choices=EMOTIONS, blank=True)
    
    # Merge functionality
    is_merged = models.BooleanField(default=False)
    merged_group_id = models.CharField(max_length=50, null=True, blank=True)
    merged_trades_count = models.IntegerField(default=1)
    original_trades_data = models.JSONField(null=True, blank=True)  # Store original trade data for unmerging
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-open_date']

    def __str__(self):
        return f"{self.asset} - {self.trade_type} - {self.open_date.strftime('%Y-%m-%d')}"

    @property
    def date_time(self):
        """Backward compatibility"""
        return self.open_date

    def get_asset_display_with_flag(self):
        """Get asset display name with flag"""
        for code, name, flag in FOREX_PAIRS:
            if code == self.asset:
                return f"{flag} {name}"
        return self.asset
    @property
    def profit_loss(self):
        # Use manual profit if provided
        if self.profit is not None:
            return self.profit
            
        if not self.exit_price:
            return None
        
        if self.trade_type == 'BUY':
            gross_profit = (self.exit_price - self.entry_price) * self.position_size
        else:  # SELL
            gross_profit = (self.entry_price - self.exit_price) * self.position_size
            
        # Subtract commission and swap
        return gross_profit - self.commission - self.swap

    @property
    def profit_loss_percentage(self):
        if self.profit is not None:
            return (self.profit / (self.entry_price * self.position_size)) * 100
            
        if not self.exit_price:
            return None
        
        if self.trade_type == 'BUY':
            return ((self.exit_price - self.entry_price) / self.entry_price) * 100
        else:  # SELL
            return ((self.entry_price - self.exit_price) / self.entry_price) * 100

    @property
    def is_profitable(self):
        pl = self.profit_loss
        return pl > 0 if pl is not None else None

    @property
    def risk_reward_ratio(self):
        if not self.stop_loss or not self.take_profit:
            return None
            
        if self.trade_type == 'BUY':
            risk = abs(self.entry_price - self.stop_loss)
            reward = abs(self.take_profit - self.entry_price)
        else:  # SELL
            risk = abs(self.stop_loss - self.entry_price)
            reward = abs(self.entry_price - self.take_profit)
            
        return reward / risk if risk > 0 else None

    def get_tags_list(self):
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
    
    def can_merge_with(self, other_trade):
        """Check if this trade can be merged with another trade"""
        return (
            self.asset == other_trade.asset and
            self.trade_type == other_trade.trade_type and
            not self.is_merged and
            not other_trade.is_merged
        )