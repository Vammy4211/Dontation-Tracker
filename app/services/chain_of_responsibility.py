"""
Chain of Responsibility Pattern - Donation Processing Pipeline

The Chain of Responsibility Pattern passes requests along a chain of handlers.
Each handler decides either to process the request or pass it to the next handler.
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
from ..models.donation import Donation
from ..models.user import User
from ..models.campaign import Campaign


class ProcessingResult(Enum):
    """Result of processing step"""
    SUCCESS = "success"
    FAILURE = "failure"
    CONTINUE = "continue"
    STOP = "stop"


class DonationProcessingRequest:
    """
    CHAIN OF RESPONSIBILITY - Request object for donation processing
    
    Contains all data needed for donation processing pipeline.
    """
    
    def __init__(self, donation: Donation, donor: User, campaign: Campaign, 
                 payment_data: Dict[str, Any]):
        """
        Initialize donation processing request
        
        Args:
            donation: Donation to process
            donor: Donor making the donation
            campaign: Campaign receiving the donation
            payment_data: Payment information
        """
        self.donation = donation
        self.donor = donor
        self.campaign = campaign
        self.payment_data = payment_data
        self.processing_context = {}
        self.errors = []
        self.warnings = []
        self.processing_log = []
        self.created_at = datetime.utcnow()
    
    def add_error(self, error: str, handler: str = None) -> None:
        """Add error to request"""
        self.errors.append({
            'message': error,
            'handler': handler,
            'timestamp': datetime.utcnow()
        })
    
    def add_warning(self, warning: str, handler: str = None) -> None:
        """Add warning to request"""
        self.warnings.append({
            'message': warning,
            'handler': handler,
            'timestamp': datetime.utcnow()
        })
    
    def log_processing_step(self, handler: str, result: ProcessingResult, 
                           message: str = "") -> None:
        """Log processing step"""
        self.processing_log.append({
            'handler': handler,
            'result': result.value,
            'message': message,
            'timestamp': datetime.utcnow()
        })
    
    def has_errors(self) -> bool:
        """Check if request has errors"""
        return len(self.errors) > 0
    
    def get_context_value(self, key: str, default=None):
        """Get value from processing context"""
        return self.processing_context.get(key, default)
    
    def set_context_value(self, key: str, value: Any) -> None:
        """Set value in processing context"""
        self.processing_context[key] = value


class DonationHandler(ABC):
    """
    CHAIN OF RESPONSIBILITY - Abstract donation handler
    
    Base class for all donation processing handlers.
    """
    
    def __init__(self):
        self._next_handler: Optional['DonationHandler'] = None
        self.handler_name = self.__class__.__name__
    
    def set_next(self, handler: 'DonationHandler') -> 'DonationHandler':
        """
        Set the next handler in the chain
        
        Args:
            handler: Next handler
            
        Returns:
            The handler that was set (for chaining)
        """
        self._next_handler = handler
        return handler
    
    def handle(self, request: DonationProcessingRequest) -> ProcessingResult:
        """
        Handle the donation processing request
        
        Args:
            request: Processing request
            
        Returns:
            Processing result
        """
        try:
            result = self._process(request)
            request.log_processing_step(self.handler_name, result)
            
            # If processing failed, stop the chain
            if result == ProcessingResult.FAILURE:
                return result
            
            # If we should stop processing, return success
            if result == ProcessingResult.STOP:
                return ProcessingResult.SUCCESS
            
            # Continue to next handler if available
            if self._next_handler and result in [ProcessingResult.SUCCESS, ProcessingResult.CONTINUE]:
                return self._next_handler.handle(request)
            
            return result
        
        except Exception as e:
            request.add_error(f"Unexpected error in {self.handler_name}: {str(e)}", self.handler_name)
            request.log_processing_step(self.handler_name, ProcessingResult.FAILURE, str(e))
            return ProcessingResult.FAILURE
    
    @abstractmethod
    def _process(self, request: DonationProcessingRequest) -> ProcessingResult:
        """
        Process the request - implemented by concrete handlers
        
        Args:
            request: Processing request
            
        Returns:
            Processing result
        """
        pass


class ValidationHandler(DonationHandler):
    """
    CHAIN OF RESPONSIBILITY - Validation Handler
    
    Validates donation data before processing.
    """
    
    def _process(self, request: DonationProcessingRequest) -> ProcessingResult:
        """Validate donation request"""
        # Validate donation amount
        if request.donation.amount <= 0:
            request.add_error("Donation amount must be greater than 0", self.handler_name)
            return ProcessingResult.FAILURE
        
        # Validate maximum donation amount
        max_donation = 10000.0  # $10,000 limit
        if request.donation.amount > max_donation:
            request.add_error(f"Donation amount exceeds maximum limit of ${max_donation}", self.handler_name)
            return ProcessingResult.FAILURE
        
        # Validate campaign is active
        if request.campaign.status != 'active':
            request.add_error("Cannot donate to inactive campaign", self.handler_name)
            return ProcessingResult.FAILURE
        
        # Check if campaign has ended
        if request.campaign.end_date and request.campaign.end_date < datetime.utcnow():
            request.add_error("Campaign has ended", self.handler_name)
            return ProcessingResult.FAILURE
        
        # Validate donor is active
        if not request.donor.is_active:
            request.add_error("Donor account is inactive", self.handler_name)
            return ProcessingResult.FAILURE
        
        # Check if donation would exceed campaign goal
        if request.campaign.goal_amount:
            total_after_donation = request.campaign.current_amount + request.donation.amount
            if total_after_donation > request.campaign.goal_amount * 1.1:  # Allow 10% overage
                request.add_warning(
                    f"Donation would exceed campaign goal by ${total_after_donation - request.campaign.goal_amount}",
                    self.handler_name
                )
        
        request.log_processing_step(self.handler_name, ProcessingResult.SUCCESS, "Validation passed")
        return ProcessingResult.SUCCESS


class DuplicateCheckHandler(DonationHandler):
    """
    CHAIN OF RESPONSIBILITY - Duplicate Check Handler
    
    Checks for duplicate donations from the same donor.
    """
    
    def __init__(self, time_window_minutes: int = 5):
        super().__init__()
        self.time_window_minutes = time_window_minutes
    
    def _process(self, request: DonationProcessingRequest) -> ProcessingResult:
        """Check for duplicate donations"""
        # In a real implementation, this would query the database
        # For demo purposes, we'll simulate the check
        
        cutoff_time = datetime.utcnow().timestamp() - (self.time_window_minutes * 60)
        request.set_context_value('duplicate_check_cutoff', cutoff_time)
        
        # Simulate duplicate check logic
        # This would typically check recent donations from the same donor to the same campaign
        duplicate_key = f"{request.donor.id}_{request.campaign.id}_{request.donation.amount}"
        request.set_context_value('duplicate_key', duplicate_key)
        
        # For demo, assume no duplicates found
        request.log_processing_step(
            self.handler_name, 
            ProcessingResult.SUCCESS, 
            f"No duplicates found in {self.time_window_minutes} minute window"
        )
        return ProcessingResult.SUCCESS


class FraudDetectionHandler(DonationHandler):
    """
    CHAIN OF RESPONSIBILITY - Fraud Detection Handler
    
    Performs fraud detection checks on donations.
    """
    
    def _process(self, request: DonationProcessingRequest) -> ProcessingResult:
        """Perform fraud detection"""
        fraud_score = 0
        fraud_reasons = []
        
        # Check 1: Large amount from new donor
        if request.donation.amount > 1000 and self._is_new_donor(request.donor):
            fraud_score += 30
            fraud_reasons.append("Large amount from new donor")
        
        # Check 2: Multiple large donations in short time
        if self._has_recent_large_donations(request.donor):
            fraud_score += 25
            fraud_reasons.append("Multiple large donations recently")
        
        # Check 3: Suspicious payment patterns
        if self._has_suspicious_payment_pattern(request.payment_data):
            fraud_score += 20
            fraud_reasons.append("Suspicious payment pattern")
        
        # Check 4: Donation amount exactly matches common fraud amounts
        suspicious_amounts = [999.99, 1000.00, 5000.00, 9999.99]
        if request.donation.amount in suspicious_amounts:
            fraud_score += 15
            fraud_reasons.append("Donation amount matches common fraud pattern")
        
        # Check 5: Rapid-fire donations
        if self._has_rapid_donations(request.donor):
            fraud_score += 10
            fraud_reasons.append("Rapid consecutive donations")
        
        request.set_context_value('fraud_score', fraud_score)
        request.set_context_value('fraud_reasons', fraud_reasons)
        
        # High fraud score - reject
        if fraud_score >= 70:
            request.add_error(f"High fraud risk (score: {fraud_score}): {', '.join(fraud_reasons)}", self.handler_name)
            return ProcessingResult.FAILURE
        
        # Medium fraud score - flag for review
        elif fraud_score >= 40:
            request.add_warning(f"Medium fraud risk (score: {fraud_score}): {', '.join(fraud_reasons)}", self.handler_name)
            request.donation.requires_review = True
        
        request.log_processing_step(
            self.handler_name, 
            ProcessingResult.SUCCESS, 
            f"Fraud check passed (score: {fraud_score})"
        )
        return ProcessingResult.SUCCESS
    
    def _is_new_donor(self, donor: User) -> bool:
        """Check if donor is new (simplified logic)"""
        # In real implementation, check donor's donation history
        return True  # Simplified for demo
    
    def _has_recent_large_donations(self, donor: User) -> bool:
        """Check for recent large donations (simplified logic)"""
        # In real implementation, check recent donation history
        return False  # Simplified for demo
    
    def _has_suspicious_payment_pattern(self, payment_data: Dict) -> bool:
        """Check for suspicious payment patterns"""
        # Check for common fraud indicators in payment data
        if 'card_number' in payment_data:
            card_number = payment_data['card_number']
            # Check for test card numbers or patterns
            test_patterns = ['4111111111111111', '4000000000000000']
            return any(pattern in card_number for pattern in test_patterns)
        return False
    
    def _has_rapid_donations(self, donor: User) -> bool:
        """Check for rapid consecutive donations"""
        # In real implementation, check timing of recent donations
        return False  # Simplified for demo


class PaymentProcessingHandler(DonationHandler):
    """
    CHAIN OF RESPONSIBILITY - Payment Processing Handler
    
    Processes the actual payment for the donation.
    """
    
    def __init__(self, payment_processor):
        super().__init__()
        self.payment_processor = payment_processor
    
    def _process(self, request: DonationProcessingRequest) -> ProcessingResult:
        """Process payment"""
        try:
            # Extract payment method from payment data
            payment_method = request.payment_data.get('method', 'credit_card')
            amount = request.donation.amount
            
            # Process payment using the payment processor
            payment_result = self.payment_processor.process_payment(
                payment_method, 
                amount, 
                request.payment_data
            )
            
            # Store payment result in context
            request.set_context_value('payment_result', payment_result)
            
            if payment_result['success']:
                # Store transaction details
                request.donation.transaction_id = payment_result.get('transaction_id')
                request.donation.payment_method = payment_result.get('payment_method')
                request.donation.payment_fee = payment_result.get('fee', 0)
                
                request.log_processing_step(
                    self.handler_name, 
                    ProcessingResult.SUCCESS, 
                    f"Payment processed: {payment_result.get('transaction_id')}"
                )
                return ProcessingResult.SUCCESS
            else:
                request.add_error(
                    f"Payment failed: {payment_result.get('error', 'Unknown error')}", 
                    self.handler_name
                )
                return ProcessingResult.FAILURE
        
        except Exception as e:
            request.add_error(f"Payment processing error: {str(e)}", self.handler_name)
            return ProcessingResult.FAILURE


class DatabaseStorageHandler(DonationHandler):
    """
    CHAIN OF RESPONSIBILITY - Database Storage Handler
    
    Stores the donation in the database.
    """
    
    def __init__(self, donation_repository):
        super().__init__()
        self.donation_repository = donation_repository
    
    def _process(self, request: DonationProcessingRequest) -> ProcessingResult:
        """Store donation in database"""
        try:
            # Set donation status based on processing
            if request.donation.requires_review:
                request.donation.status = 'pending_review'
            else:
                request.donation.status = 'completed'
            
            # Store creation timestamp
            request.donation.created_at = datetime.utcnow()
            
            # Save to database
            saved_donation = self.donation_repository.create(request.donation)
            request.set_context_value('saved_donation', saved_donation)
            
            request.log_processing_step(
                self.handler_name, 
                ProcessingResult.SUCCESS, 
                f"Donation saved with ID: {saved_donation.id}"
            )
            return ProcessingResult.SUCCESS
        
        except Exception as e:
            request.add_error(f"Database storage error: {str(e)}", self.handler_name)
            return ProcessingResult.FAILURE


class CampaignUpdateHandler(DonationHandler):
    """
    CHAIN OF RESPONSIBILITY - Campaign Update Handler
    
    Updates campaign totals after successful donation.
    """
    
    def __init__(self, campaign_repository):
        super().__init__()
        self.campaign_repository = campaign_repository
    
    def _process(self, request: DonationProcessingRequest) -> ProcessingResult:
        """Update campaign totals"""
        try:
            # Only update if donation is completed (not pending review)
            if request.donation.status == 'completed':
                # Update campaign amounts
                request.campaign.current_amount += request.donation.amount
                request.campaign.donation_count += 1
                request.campaign.updated_at = datetime.utcnow()
                
                # Check if goal is reached
                if (request.campaign.goal_amount and 
                    request.campaign.current_amount >= request.campaign.goal_amount):
                    request.campaign.status = 'completed'
                    request.add_warning("Campaign goal reached!", self.handler_name)
                
                # Save updated campaign
                updated_campaign = self.campaign_repository.update(request.campaign)
                request.set_context_value('updated_campaign', updated_campaign)
                
                request.log_processing_step(
                    self.handler_name, 
                    ProcessingResult.SUCCESS, 
                    f"Campaign updated: ${request.campaign.current_amount} total"
                )
            else:
                request.log_processing_step(
                    self.handler_name, 
                    ProcessingResult.SUCCESS, 
                    "Campaign not updated - donation pending review"
                )
            
            return ProcessingResult.SUCCESS
        
        except Exception as e:
            request.add_error(f"Campaign update error: {str(e)}", self.handler_name)
            return ProcessingResult.FAILURE


class NotificationHandler(DonationHandler):
    """
    CHAIN OF RESPONSIBILITY - Notification Handler
    
    Sends notifications after successful donation processing.
    """
    
    def __init__(self, event_manager):
        super().__init__()
        self.event_manager = event_manager
    
    def _process(self, request: DonationProcessingRequest) -> ProcessingResult:
        """Send notifications"""
        try:
            # Trigger donation events
            if request.donation.status == 'completed':
                self.event_manager.notify_donation_completed(request.donation)
            elif request.donation.status == 'pending_review':
                self.event_manager.notify_donation_pending_review(request.donation)
            
            # Check if campaign goal was reached
            if (request.campaign.status == 'completed' and 
                request.get_context_value('updated_campaign')):
                self.event_manager.notify_campaign_goal_reached(request.campaign)
            
            request.log_processing_step(
                self.handler_name, 
                ProcessingResult.SUCCESS, 
                "Notifications sent"
            )
            return ProcessingResult.SUCCESS
        
        except Exception as e:
            request.add_error(f"Notification error: {str(e)}", self.handler_name)
            # Don't fail the entire process for notification errors
            request.add_warning("Notifications failed but donation was processed", self.handler_name)
            return ProcessingResult.SUCCESS


class DonationProcessingPipeline:
    """
    CHAIN OF RESPONSIBILITY - Main donation processing pipeline
    
    Orchestrates the entire donation processing chain.
    """
    
    def __init__(self, payment_processor, donation_repository, 
                 campaign_repository, event_manager):
        """
        Initialize processing pipeline
        
        Args:
            payment_processor: Payment processing service
            donation_repository: Donation repository
            campaign_repository: Campaign repository
            event_manager: Event notification manager
        """
        # Create the chain of handlers
        self.validation_handler = ValidationHandler()
        self.duplicate_check_handler = DuplicateCheckHandler()
        self.fraud_detection_handler = FraudDetectionHandler()
        self.payment_handler = PaymentProcessingHandler(payment_processor)
        self.storage_handler = DatabaseStorageHandler(donation_repository)
        self.campaign_update_handler = CampaignUpdateHandler(campaign_repository)
        self.notification_handler = NotificationHandler(event_manager)
        
        # Chain the handlers together
        self.validation_handler.set_next(self.duplicate_check_handler) \
                              .set_next(self.fraud_detection_handler) \
                              .set_next(self.payment_handler) \
                              .set_next(self.storage_handler) \
                              .set_next(self.campaign_update_handler) \
                              .set_next(self.notification_handler)
    
    def process_donation(self, donation: Donation, donor: User, 
                        campaign: Campaign, payment_data: Dict[str, Any]) -> DonationProcessingRequest:
        """
        Process a donation through the entire pipeline
        
        Args:
            donation: Donation to process
            donor: Donor making the donation
            campaign: Campaign receiving the donation
            payment_data: Payment information
            
        Returns:
            Processing request with results
        """
        # Create processing request
        request = DonationProcessingRequest(donation, donor, campaign, payment_data)
        
        # Start processing through the chain
        result = self.validation_handler.handle(request)
        
        # Set final result
        request.set_context_value('final_result', result)
        request.set_context_value('completed_at', datetime.utcnow())
        
        return request
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get status information about the pipeline"""
        return {
            'handlers': [
                'ValidationHandler',
                'DuplicateCheckHandler', 
                'FraudDetectionHandler',
                'PaymentProcessingHandler',
                'DatabaseStorageHandler',
                'CampaignUpdateHandler',
                'NotificationHandler'
            ],
            'total_handlers': 7
        }


# Usage example:
"""
# Create pipeline
pipeline = DonationProcessingPipeline(
    payment_processor=payment_processor,
    donation_repository=donation_repository,
    campaign_repository=campaign_repository,
    event_manager=event_manager
)

# Process donation
result = pipeline.process_donation(donation, donor, campaign, payment_data)

# Check results
if result.has_errors():
    print(f"Processing failed: {result.errors}")
else:
    print(f"Donation processed successfully: {result.get_context_value('saved_donation').id}")

# View processing log
for step in result.processing_log:
    print(f"{step['handler']}: {step['result']} - {step['message']}")
"""