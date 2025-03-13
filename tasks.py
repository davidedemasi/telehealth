import random
import time
from celery import Celery

# Initialize Celery
celery = Celery(
    'telehealth',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

# Celery configuration
celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

@celery.task(bind=True, max_retries=3)
def send_notification(self, patient_id, patient_name, patient_contact, notification_type='email'):
    """
    Send notification to patient.
    
    Args:
        patient_id (int): Patient ID
        patient_name (str): Patient name
        patient_contact (str): Patient email or phone
        notification_type (str): Type of notification (email/sms)
    
    Returns:
        str: Message indicating success or failure
    """
    try:
        # Simulate a task that sometimes fails (25% chance)
        if random.random() < 0.25:
            raise Exception("Simulated notification failure")
        
        # Simulate processing time
        time.sleep(2)
        
        message = f"Notification sent successfully to {patient_name} ({patient_contact}) via {notification_type}"
        print(message)
        return message
    
    except Exception as e:
        # Log the error
        error_message = f"Failed to send notification to patient {patient_id}: {str(e)}"
        print(error_message)
        
        # Retry the task (with exponential backoff)
        retry_in = 2 ** self.request.retries
        raise self.retry(exc=e, countdown=retry_in)
