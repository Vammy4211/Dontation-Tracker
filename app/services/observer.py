"""
Observer Pattern - Event System for Donation Notifications

The Observer Pattern defines a one-to-many dependency between objects
so that when one object changes state, all dependents are notified automatically.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime
import logging


class Observer(ABC):
    """
    OBSERVER PATTERN - Abstract Observer Interface
    
    Defines the interface that all observers must implement.
    Observers are notified when events occur in the system.
    """
    
    @abstractmethod
    def update(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Handle event notification
        
        Args:
            event_type: Type of event that occurred
            data: Event data
        """
        pass


class Subject(ABC):
    """
    OBSERVER PATTERN - Abstract Subject Interface
    
    Defines the interface for managing observers and
    notifying them of events.
    """
    
    def __init__(self):
        self._observers: List[Observer] = []
    
    def attach(self, observer: Observer) -> None:
        """
        Attach an observer to the subject
        
        Args:
            observer: Observer to attach
        """
        if observer not in self._observers:
            self._observers.append(observer)
    
    def detach(self, observer: Observer) -> None:
        """
        Detach an observer from the subject
        
        Args:
            observer: Observer to detach
        """
        if observer in self._observers:
            self._observers.remove(observer)
    
    def notify(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Notify all observers of an event
        
        Args:
            event_type: Type of event
            data: Event data
        """
        for observer in self._observers:
            try:
                observer.update(event_type, data)
            except Exception as e:
                logging.error(f"Observer notification failed: {e}")


class DonationEventManager(Subject):
    """
    OBSERVER PATTERN - Concrete Subject for Donation Events
    
    Manages donation-related events and notifies observers
    when donations are created, completed, or refunded.
    """
    
    def __init__(self):
        super().__init__()
        self._event_log: List[Dict] = []
    
    def donation_created(self, donation_data: Dict) -> None:
        """
        Notify observers when a donation is created
        
        Args:
            donation_data: Donation information
        """
        event_data = {
            'donation_id': donation_data.get('donation_id'),
            'donor_id': donation_data.get('donor_id'),
            'campaign_id': donation_data.get('campaign_id'),
            'amount': donation_data.get('amount'),
            'timestamp': datetime.utcnow(),
            'is_anonymous': donation_data.get('is_anonymous', False)
        }
        
        self._log_event('donation_created', event_data)
        self.notify('donation_created', event_data)
    
    def donation_completed(self, donation_data: Dict) -> None:
        """
        Notify observers when a donation is completed
        
        Args:
            donation_data: Donation information
        """
        event_data = {
            'donation_id': donation_data.get('donation_id'),
            'donor_id': donation_data.get('donor_id'),
            'campaign_id': donation_data.get('campaign_id'),
            'amount': donation_data.get('amount'),
            'transaction_id': donation_data.get('transaction_id'),
            'timestamp': datetime.utcnow()
        }
        
        self._log_event('donation_completed', event_data)
        self.notify('donation_completed', event_data)
    
    def donation_refunded(self, donation_data: Dict) -> None:
        """
        Notify observers when a donation is refunded
        
        Args:
            donation_data: Donation information
        """
        event_data = {
            'donation_id': donation_data.get('donation_id'),
            'donor_id': donation_data.get('donor_id'),
            'campaign_id': donation_data.get('campaign_id'),
            'amount': donation_data.get('amount'),
            'refund_id': donation_data.get('refund_id'),
            'timestamp': datetime.utcnow()
        }
        
        self._log_event('donation_refunded', event_data)
        self.notify('donation_refunded', event_data)
    
    def campaign_goal_reached(self, campaign_data: Dict) -> None:
        """
        Notify observers when a campaign reaches its goal
        
        Args:
            campaign_data: Campaign information
        """
        event_data = {
            'campaign_id': campaign_data.get('campaign_id'),
            'title': campaign_data.get('title'),
            'goal_amount': campaign_data.get('goal_amount'),
            'current_amount': campaign_data.get('current_amount'),
            'creator_id': campaign_data.get('creator_id'),
            'timestamp': datetime.utcnow()
        }
        
        self._log_event('campaign_goal_reached', event_data)
        self.notify('campaign_goal_reached', event_data)
    
    def _log_event(self, event_type: str, data: Dict) -> None:
        """
        Log event for debugging and audit purposes
        
        Args:
            event_type: Type of event
            data: Event data
        """
        log_entry = {
            'event_type': event_type,
            'data': data,
            'logged_at': datetime.utcnow()
        }
        self._event_log.append(log_entry)
        
        # Keep only last 1000 events
        if len(self._event_log) > 1000:
            self._event_log = self._event_log[-1000:]
    
    def get_event_log(self, limit: int = 50) -> List[Dict]:
        """
        Get recent events from log
        
        Args:
            limit: Maximum number of events to return
            
        Returns:
            List of recent events
        """
        return self._event_log[-limit:]


class EmailNotificationObserver(Observer):
    """
    OBSERVER PATTERN - Concrete Observer for Email Notifications
    
    Sends email notifications when donation events occur.
    """
    
    def __init__(self, email_service=None):
        self.email_service = email_service or MockEmailService()
        self.enabled = True
    
    def update(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Handle donation events by sending email notifications
        
        Args:
            event_type: Type of event
            data: Event data
        """
        if not self.enabled:
            return
        
        try:
            if event_type == 'donation_completed':
                self._send_donation_receipt(data)
                self._notify_campaign_creator(data)
            
            elif event_type == 'campaign_goal_reached':
                self._send_goal_reached_notification(data)
            
            elif event_type == 'donation_refunded':
                self._send_refund_notification(data)
                
        except Exception as e:
            logging.error(f"Email notification failed: {e}")
    
    def _send_donation_receipt(self, data: Dict) -> None:
        """Send donation receipt to donor"""
        self.email_service.send_email(
            to=f"donor_{data['donor_id']}@example.com",  # Would get actual email
            subject="Thank you for your donation!",
            template="donation_receipt",
            data=data
        )
    
    def _notify_campaign_creator(self, data: Dict) -> None:
        """Notify campaign creator of new donation"""
        self.email_service.send_email(
            to=f"creator_{data['campaign_id']}@example.com",  # Would get actual email
            subject="New donation received!",
            template="new_donation_notification",
            data=data
        )
    
    def _send_goal_reached_notification(self, data: Dict) -> None:
        """Send goal reached notification"""
        self.email_service.send_email(
            to=f"creator_{data['creator_id']}@example.com",
            subject="🎉 Campaign goal reached!",
            template="goal_reached",
            data=data
        )
    
    def _send_refund_notification(self, data: Dict) -> None:
        """Send refund notification to donor"""
        self.email_service.send_email(
            to=f"donor_{data['donor_id']}@example.com",
            subject="Donation refund processed",
            template="refund_notification",
            data=data
        )
    
    def disable(self) -> None:
        """Disable email notifications"""
        self.enabled = False
    
    def enable(self) -> None:
        """Enable email notifications"""
        self.enabled = True


class CampaignUpdateObserver(Observer):
    """
    OBSERVER PATTERN - Concrete Observer for Campaign Updates
    
    Updates campaign statistics when donations occur.
    """
    
    def __init__(self, campaign_repository=None):
        from .repositories import CampaignRepository
        self.campaign_repository = campaign_repository or CampaignRepository()
    
    def update(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Handle donation events by updating campaign data
        
        Args:
            event_type: Type of event
            data: Event data
        """
        try:
            if event_type == 'donation_completed':
                self._update_campaign_totals(data)
            
            elif event_type == 'donation_refunded':
                self._handle_donation_refund(data)
                
        except Exception as e:
            logging.error(f"Campaign update failed: {e}")
    
    def _update_campaign_totals(self, data: Dict) -> None:
        """
        Update campaign totals when donation is completed
        
        Args:
            data: Donation event data
        """
        campaign_id = data.get('campaign_id')
        amount = data.get('amount', 0)
        donor_id = data.get('donor_id')
        
        campaign = self.campaign_repository.get_by_id(campaign_id)
        if campaign:
            # Add donation to campaign
            campaign.add_donation(amount, donor_id)
            
            # Update campaign in database
            self.campaign_repository.update(campaign)
            
            # Check if goal is reached and trigger event
            if campaign.is_completed:
                from .observer import DonationEventManager
                event_manager = DonationEventManager()
                event_manager.campaign_goal_reached({
                    'campaign_id': campaign.campaign_id,
                    'title': campaign.title,
                    'goal_amount': campaign.goal_amount,
                    'current_amount': campaign.current_amount,
                    'creator_id': campaign.creator_id
                })
    
    def _handle_donation_refund(self, data: Dict) -> None:
        """
        Handle donation refund by updating campaign totals
        
        Args:
            data: Refund event data
        """
        campaign_id = data.get('campaign_id')
        amount = data.get('amount', 0)
        
        campaign = self.campaign_repository.get_by_id(campaign_id)
        if campaign:
            # Subtract refunded amount
            campaign._current_amount = max(0, campaign._current_amount - amount)
            campaign._donation_count = max(0, campaign._donation_count - 1)
            
            # Update campaign in database
            self.campaign_repository.update(campaign)


class AnalyticsObserver(Observer):
    """
    OBSERVER PATTERN - Concrete Observer for Analytics
    
    Tracks donation analytics and metrics.
    """
    
    def __init__(self):
        self.metrics = {
            'total_donations': 0,
            'total_amount': 0.0,
            'donations_by_hour': {},
            'donations_by_campaign': {},
            'refunds_count': 0,
            'refunds_amount': 0.0
        }
    
    def update(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Handle events by updating analytics metrics
        
        Args:
            event_type: Type of event
            data: Event data
        """
        try:
            if event_type == 'donation_completed':
                self._track_donation(data)
            
            elif event_type == 'donation_refunded':
                self._track_refund(data)
                
        except Exception as e:
            logging.error(f"Analytics update failed: {e}")
    
    def _track_donation(self, data: Dict) -> None:
        """Track completed donation in analytics"""
        amount = data.get('amount', 0)
        campaign_id = data.get('campaign_id')
        timestamp = data.get('timestamp', datetime.utcnow())
        
        # Update total metrics
        self.metrics['total_donations'] += 1
        self.metrics['total_amount'] += amount
        
        # Track by hour
        hour_key = timestamp.strftime('%Y-%m-%d %H:00')
        if hour_key not in self.metrics['donations_by_hour']:
            self.metrics['donations_by_hour'][hour_key] = {'count': 0, 'amount': 0.0}
        
        self.metrics['donations_by_hour'][hour_key]['count'] += 1
        self.metrics['donations_by_hour'][hour_key]['amount'] += amount
        
        # Track by campaign
        if campaign_id not in self.metrics['donations_by_campaign']:
            self.metrics['donations_by_campaign'][campaign_id] = {'count': 0, 'amount': 0.0}
        
        self.metrics['donations_by_campaign'][campaign_id]['count'] += 1
        self.metrics['donations_by_campaign'][campaign_id]['amount'] += amount
    
    def _track_refund(self, data: Dict) -> None:
        """Track refund in analytics"""
        amount = data.get('amount', 0)
        
        self.metrics['refunds_count'] += 1
        self.metrics['refunds_amount'] += amount
    
    def get_metrics(self) -> Dict:
        """Get current analytics metrics"""
        return self.metrics.copy()


class MockEmailService:
    """Mock email service for testing"""
    
    def __init__(self):
        self.sent_emails = []
    
    def send_email(self, to: str, subject: str, template: str, data: Dict) -> None:
        """Mock email sending"""
        email = {
            'to': to,
            'subject': subject,
            'template': template,
            'data': data,
            'sent_at': datetime.utcnow()
        }
        self.sent_emails.append(email)
        print(f"📧 Email sent: {subject} to {to}")
    
    def get_sent_emails(self) -> List[Dict]:
        """Get list of sent emails"""
        return self.sent_emails.copy()


# Global event manager instance (Singleton-like)
_donation_event_manager = None

def get_donation_event_manager() -> DonationEventManager:
    """
    Get global donation event manager instance
    
    Returns:
        DonationEventManager instance
    """
    global _donation_event_manager
    if _donation_event_manager is None:
        _donation_event_manager = DonationEventManager()
        
        # Attach default observers
        _donation_event_manager.attach(EmailNotificationObserver())
        _donation_event_manager.attach(CampaignUpdateObserver())
        _donation_event_manager.attach(AnalyticsObserver())
    
    return _donation_event_manager


# Usage example:
"""
# Get event manager and trigger events
event_manager = get_donation_event_manager()

# When a donation is completed
donation_data = {
    'donation_id': 'donation_123',
    'donor_id': 'donor_456',
    'campaign_id': 'campaign_789',
    'amount': 100.0,
    'transaction_id': 'txn_abc123'
}

event_manager.donation_completed(donation_data)

# All observers will be notified:
# - EmailNotificationObserver sends receipt and creator notification
# - CampaignUpdateObserver updates campaign totals
# - AnalyticsObserver tracks metrics
"""