from typing import Dict, Any, List
from .rule_engine import RuleEngine
from core.utils.logger_config import get_logger

logger = get_logger(__name__)

class Organizer:
    def __init__(self, rules_json: Dict[str, Any], use_ml_model: bool = False, model: Any = None):
        """
        Initializes the Organizer with the given rules and optional ML model.
        """
        self.rule_engine = RuleEngine(rules_json, use_ml_model, model)
        self.action_handlers = {
            "move_to_folder": self._move_to_folder,
            "delete": self._delete_email,
            "add_category": self._add_category,
            "add_flag": self._add_flag,
            "remove_flag": self._remove_flag,
            "forward_to": self._forward_to,
            "reply_with_template": self._reply_with_template,
            "mark_as_read": self._mark_as_read,
            "mark_as_unread": self._mark_as_unread,
            "set_importance": self._set_importance,
            "stop_processing": self._stop_processing, # Handle this directly in organize_email
            "no_op": self._no_op,
            # Add more action handlers here
        }

    def organize_email(self, email_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Organizes a single email based on the rules.

        Args:
            email_data (Dict[str, Any]): Email attributes

        Returns:
            List[Dict[str, Any]]: List of actions that were decided and (attempted to be) applied.
        """
        actions_with_priority = self.rule_engine.evaluate(email_data)
        applied_actions = []
        stop_processing = False

        for item in actions_with_priority:
            if stop_processing:
                logger.info(f"Stopping further action processing for email '{email_data.get('subject', '<No Subject>')}' due to 'stop_processing' action.")
                break

            action = item['action']
            action_type = action.get("type")

            if action_type in self.action_handlers:
                handler = self.action_handlers[action_type]
                success = handler(email_data, action)
                if success:
                    applied_actions.append(action)
                else:
                    logger.error(f"Failed to apply action '{action_type}' on email '{email_data.get('subject', '<No Subject>')}'. Action details: {action}")

                if action_type == "stop_processing":
                    stop_processing = True
            else:
                logger.warning(f"Unknown action type '{action_type}' encountered for email '{email_data.get('subject', '<No Subject>')}'. Action details: {action}")

        return applied_actions

    def _move_to_folder(self, email_data: Dict[str, Any], action: Dict[str, Any]) -> bool:
        folder_name = action.get("target")
        if folder_name:
            logger.info(f"Simulating move to folder '{folder_name}' for email '{email_data.get('subject', '<No Subject>')}'")
            return True # Simulate success
        else:
            logger.error(f"'target' folder missing for 'move_to_folder' action on email '{email_data.get('subject', '<No Subject>')}'")
            return False

    def _delete_email(self, email_data: Dict[str, Any], action: Dict[str, Any]) -> bool:
        logger.warning(f"Simulating deletion of email '{email_data.get('subject', '<No Subject>')}'")
        return True # Simulate success

    def _add_category(self, email_data: Dict[str, Any], action: Dict[str, Any]) -> bool:
        category_name = action.get("category_name")
        if category_name:
            logger.info(f"Simulating adding category '{category_name}' to email '{email_data.get('subject', '<No Subject>')}'")
            return True
        else:
            logger.error(f"'category_name' missing for 'add_category' action on email '{email_data.get('subject', '<No Subject>')}'")
            return False

    def _add_flag(self, email_data: Dict[str, Any], action: Dict[str, Any]) -> bool:
        flag_type = action.get("flag_type")
        if flag_type:
            logger.info(f"Simulating adding flag '{flag_type}' to email '{email_data.get('subject', '<No Subject>')}'")
            return True
        else:
            logger.error(f"'flag_type' missing for 'add_flag' action on email '{email_data.get('subject', '<No Subject>')}'")
            return False

    def _remove_flag(self, email_data: Dict[str, Any], action: Dict[str, Any]) -> bool:
        flag_type = action.get("flag_type")
        if flag_type:
            logger.info(f"Simulating removing flag '{flag_type}' from email '{email_data.get('subject', '<No Subject>')}'")
            return True
        else:
            logger.error(f"'flag_type' missing for 'remove_flag' action on email '{email_data.get('subject', '<No Subject>')}'")
            return False

    def _forward_to(self, email_data: Dict[str, Any], action: Dict[str, Any]) -> bool:
        target_email = action.get("target_email")
        if target_email:
            logger.info(f"Simulating forwarding email '{email_data.get('subject', '<No Subject>')}' to '{target_email}'")
            return True
        else:
            logger.error(f"'target_email' missing for 'forward_to' action on email '{email_data.get('subject', '<No Subject>')}'")
            return False

    def _reply_with_template(self, email_data: Dict[str, Any], action: Dict[str, Any]) -> bool:
        template_id = action.get("template_id")
        if template_id:
            logger.info(f"Simulating replying to email '{email_data.get('subject', '<No Subject>')}' with template '{template_id}'")
            return True
        else:
            logger.error(f"'template_id' missing for 'reply_with_template' action on email '{email_data.get('subject', '<No Subject>')}'")
            return False

    def _mark_as_read(self, email_data: Dict[str, Any], action: Dict[str, Any]) -> bool:
        logger.info(f"Simulating marking email '{email_data.get('subject', '<No Subject>')}' as read")
        return True

    def _mark_as_unread(self, email_data: Dict[str, Any], action: Dict[str, Any]) -> bool:
        logger.info(f"Simulating marking email '{email_data.get('subject', '<No Subject>')}' as unread")
        return True

    def _set_importance(self, email_data: Dict[str, Any], action: Dict[str, Any]) -> bool:
        level = action.get("level")
        if level:
            logger.info(f"Simulating setting importance to '{level}' for email '{email_data.get('subject', '<No Subject>')}'")
            return True
        else:
            logger.error(f"'level' missing for 'set_importance' action on email '{email_data.get('subject', '<No Subject>')}'")
            return False

    def _stop_processing(self, email_data: Dict[str, Any], action: Dict[str, Any]) -> bool:
        logger.info(f"Encountered 'stop_processing' action for email '{email_data.get('subject', '<No Subject>')}'")
        return True # Indicate success, as the goal is to stop

    def _no_op(self, email_data: Dict[str, Any], action: Dict[str, Any]) -> bool:
        logger.info(f"Performing no operation for email '{email_data.get('subject', '<No Subject>')}'")
        return True

    # Placeholder for real implementations of action handlers
    # def _move_to_folder(self, email_data: Dict[str, Any], folder_name: str):
    #     pass
    #
    # def _delete_email(self, email_data: Dict[str, Any]):
    #     pass
    #
    # def _apply_label(self, email_data: Dict[str, Any], label: str):
    #     pass