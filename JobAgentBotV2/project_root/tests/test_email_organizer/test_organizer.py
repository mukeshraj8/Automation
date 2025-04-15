# tests/test_email_organizer/test_organizer.py

import unittest
from unittest.mock import MagicMock
from modules.email_organizer.organizer import Organizer
import logging
import io  # Import the io module

class TestOrganizer(unittest.TestCase):

    def setUp(self):
        self.mock_rules_json = {
            "rules": [
                {
                    "id": "rule1",
                    "description": "Move important emails",
                    "priority": 1,
                    "condition_logic": "AND",
                    "conditions": [
                        {"field": "subject", "operation": "contains", "value": "Important"}
                    ],
                    "action": {"type": "move_to_folder", "target": "Important"}
                },
                {
                    "id": "rule2",
                    "description": "Delete spam emails",
                    "priority": 2,
                    "condition_logic": "AND",
                    "conditions": [
                        {"field": "from", "operation": "contains", "value": "spam@"}
                    ],
                    "action": {"type": "delete"}
                },
                {
                    "id": "rule3",
                    "description": "Stop processing for high priority",
                    "priority": 3,
                    "condition_logic": "AND",
                    "conditions": [
                        {"field": "subject", "operation": "equals", "value": "High Priority"}
                    ],
                    "action": {"type": "stop_processing"}
                },
                {
                    "id": "rule4",
                    "description": "Add a flag",
                    "priority": 4,
                    "condition_logic": "AND",
                    "conditions": [
                        {"field": "subject", "operation": "contains", "value": "Action Needed"}
                    ],
                    "action": {"type": "add_flag", "flag_type": "Urgent"}
                },
                {
                    "id": "rule5",
                    "description": "Remove a flag",
                    "priority": 5,
                    "condition_logic": "AND",
                    "conditions": [
                        {"field": "subject", "operation": "contains", "value": "Action Done"}
                    ],
                    "action": {"type": "remove_flag", "flag_type": "Urgent"}
                },
                {
                    "id": "rule6",
                    "description": "Forward email",
                    "priority": 6,
                    "condition_logic": "AND",
                    "conditions": [
                        {"field": "subject", "operation": "contains", "value": "Forward"}
                    ],
                    "action": {"type": "forward_to", "target_email": "forward@example.com"}
                },
                {
                    "id": "rule7",
                    "description": "Reply with template",
                    "priority": 7,
                    "condition_logic": "AND",
                    "conditions": [
                        {"field": "subject", "operation": "contains", "value": "Support"}
                    ],
                    "action": {"type": "reply_with_template", "template_id": "support_reply"}
                },
                {
                    "id": "rule8",
                    "description": "Mark as read",
                    "priority": 8,
                    "condition_logic": "AND",
                    "conditions": [
                        {"field": "subject", "operation": "contains", "value": "Read Me"}
                    ],
                    "action": {"type": "mark_as_read"}
                },
                {
                    "id": "rule9",
                    "description": "Mark as unread",
                    "priority": 9,
                    "condition_logic": "AND",
                    "conditions": [
                        {"field": "subject", "operation": "contains", "value": "Unread Me"}
                    ],
                    "action": {"type": "mark_as_unread"}
                },
                {
                    "id": "rule10",
                    "description": "Set importance",
                    "priority": 10,
                    "condition_logic": "AND",
                    "conditions": [
                        {"field": "subject", "operation": "contains", "value": "Urgent Matter"}
                    ],
                    "action": {"type": "set_importance", "level": "high"}
                },
                {
                    "id": "rule11",
                    "description": "No operation",
                    "priority": 11,
                    "condition_logic": "AND",
                    "conditions": [
                        {"field": "subject", "operation": "contains", "value": "No Action"}
                    ],
                    "action": {"type": "no_op"}
                }
            ]
        }

        self.mock_rule_engine = MagicMock()
        self.organizer = Organizer(self.mock_rules_json)
        self.organizer.rule_engine = self.mock_rule_engine  # Override the default with the mock
        self.logger_name = 'modules.email_organizer.organizer'  # Correct logger name
        self.log_handler = logging.StreamHandler(io.StringIO())
        self.logger = logging.getLogger(self.logger_name)
        self.logger.addHandler(self.log_handler)
        self.logger.setLevel(logging.INFO)
        self.log_output = self.log_handler.stream

    def tearDown(self):
        self.logger.removeHandler(self.log_handler)
        self.log_output.close()

    def test_organize_email_single_action(self):
        email_data = {"subject": "Important Email"}
        expected_actions = [{"type": "move_to_folder", "target": "Important"}]
        self.mock_rule_engine.evaluate.return_value = [{"priority": 1, "action": expected_actions[0]}]
        actions = self.organizer.organize_email(email_data)
        self.assertEqual(actions, expected_actions)
        self.mock_rule_engine.evaluate.assert_called_once_with(email_data)

    def _test_organize_email_apply_action(self, email_data, action, expected_log_message, log_level=logging.INFO):
        """Helper method to test apply actions."""
        self.mock_rule_engine.evaluate.return_value = [{"priority": 1, "action": action}]
        self.log_output.seek(0)
        self.log_output.truncate(0)
        self.logger.setLevel(log_level)
        self.organizer.organize_email(email_data)
        self.assertIn(expected_log_message, self.log_output.getvalue())
        self.logger.setLevel(logging.INFO)  # Reset log level

    def test_organize_email_apply_move_to_folder(self):
        email_data = {"subject": "Important Email"}
        action = {"type": "move_to_folder", "target": "MovedFolder"}
        expected_log_message = "Simulating move to folder 'MovedFolder' for email 'Important Email'"
        self._test_organize_email_apply_action(email_data, action, expected_log_message)

    def test_organize_email_apply_delete(self):
        email_data = {"from": "test@spam.com"}
        action = {"type": "delete"}
        expected_log_message = "Simulating deletion of email '<No Subject>'"
        self._test_organize_email_apply_action(email_data, action, expected_log_message, logging.WARNING)

    def test_organize_email_apply_add_flag(self):
        email_data = {"subject": "Action Needed"}
        action = {"type": "add_flag", "flag_type": "High"}
        expected_log_message = "Simulating adding flag 'High' to email 'Action Needed'"
        self._test_organize_email_apply_action(email_data, action, expected_log_message)

    def test_organize_email_apply_remove_flag(self):
        email_data = {"subject": "Action Done"}
        action = {"type": "remove_flag", "flag_type": "High"}
        expected_log_message = "Simulating removing flag 'High' from email 'Action Done'"
        self._test_organize_email_apply_action(email_data, action, expected_log_message)

    def test_organize_email_apply_forward_to(self):
        email_data = {"subject": "Forward This"}
        action = {"type": "forward_to", "target_email": "test@forward.com"}
        expected_log_message = "Simulating forwarding email 'Forward This' to 'test@forward.com'"
        self._test_organize_email_apply_action(email_data, action, expected_log_message)

    def test_organize_email_apply_reply_with_template(self):
        email_data = {"subject": "Support Request"}
        action = {"type": "reply_with_template", "template_id": "support_reply"}
        expected_log_message = "Simulating replying to email 'Support Request' with template 'support_reply'"
        self._test_organize_email_apply_action(email_data, action, expected_log_message)

    def test_organize_email_apply_mark_as_read(self):
        email_data = {"subject": "Read Me Now"}
        action = {"type": "mark_as_read"}
        expected_log_message = "Simulating marking email 'Read Me Now' as read"
        self._test_organize_email_apply_action(email_data, action, expected_log_message)

    def test_organize_email_apply_mark_as_unread(self):
        email_data = {"subject": "Unread This"}
        action = {"type": "mark_as_unread"}
        expected_log_message = "Simulating marking email 'Unread This' as unread"
        self._test_organize_email_apply_action(email_data, action, expected_log_message)

    def test_organize_email_apply_set_importance(self):
        email_data = {"subject": "Urgent Matter"}
        action = {"type": "set_importance", "level": "high"}
        expected_log_message = "Simulating setting importance to 'high' for email 'Urgent Matter'"
        self._test_organize_email_apply_action(email_data, action, expected_log_message)

    def test_organize_email_apply_no_op(self):
        email_data = {"subject": "No Action Needed"}
        action = {"type": "no_op"}
        expected_log_message = "Performing no operation for email 'No Action Needed'"
        self._test_organize_email_apply_action(email_data, action, expected_log_message)

    def test_organize_email_unknown_action(self):
        email_data = {"subject": "Unknown Action"}
        action = {"type": "unknown_action"}
        expected_log_message = "Unknown action type 'unknown_action' encountered for email 'Unknown Action'. Action details: {'type': 'unknown_action'}"
        self._test_organize_email_apply_action(email_data, action, expected_log_message, logging.WARNING)

    def test_organize_email_stop_processing_stops_further_actions(self):
        email_data = {"subject": "High Priority and Important"}
        actions = [
            {"priority": 1, "action": {"type": "move_to_folder", "target": "Important"}},
            {"priority": 2, "action": {"type": "stop_processing"}},
            {"priority": 3, "action": {"type": "delete"}}
        ]
        self.mock_rule_engine.evaluate.return_value = actions
        self.log_output.seek(0)
        self.log_output.truncate(0)
        self.organizer.organize_email(email_data)
        self.assertIn("Stopping further action processing for email 'High Priority and Important' due to 'stop_processing' action.", self.log_output.getvalue())

if __name__ == '__main__':
    unittest.main()