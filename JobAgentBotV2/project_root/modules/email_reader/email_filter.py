from email.message import Message
from typing import Optional, List

class EmailFilter:
    def __init__(
        self, 
        subject_keywords: Optional[List[str]] = None, 
        sender_keywords: Optional[List[str]] = None,
        max_attachment_size: Optional[int] = None,  # in bytes
        importance_levels: Optional[List[str]] = None  # e.g., ['high', 'urgent']
    ):
        self.subject_keywords = subject_keywords or []
        self.sender_keywords = sender_keywords or []
        self.max_attachment_size = max_attachment_size
        self.importance_levels = importance_levels or []

    def filter_email(self, msg: Message) -> bool:
        subject = msg.get('Subject', '').lower()
        sender = msg.get('From', '').lower()
        importance = msg.get('Importance', '').lower()
        priority = msg.get('X-Priority', '').lower()

        # If subject_keywords were given, check subject match
        if self.subject_keywords:
            if not any(keyword.lower() in subject for keyword in self.subject_keywords):
                return False

        # If sender_keywords were given, check sender match
        if self.sender_keywords:
            if not any(keyword.lower() in sender for keyword in self.sender_keywords):
                return False

        # If importance_levels were given, check importance match
        if self.importance_levels:
            if not (importance in self.importance_levels or priority.startswith('1')):
                return False

        # If max_attachment_size was given, check attachments
        if self.max_attachment_size is not None:
            total_attachment_size = 0
            for part in msg.iter_attachments():
                payload = part.get_payload(decode=True)
                if payload:
                    total_attachment_size += len(payload)
            
            if total_attachment_size > self.max_attachment_size:
                return False

        # If passed all provided checks
        return True

    def _get_total_attachment_size(self, msg: Message) -> int:
        """Calculate the total size of all attachments in the email."""
        total_size = 0
        for part in msg.walk():
            if part.get_content_disposition() == 'attachment':
                payload = part.get_payload(decode=True)
                if payload:  # Ensure payload is not None
                    total_size += len(payload)
        return total_size