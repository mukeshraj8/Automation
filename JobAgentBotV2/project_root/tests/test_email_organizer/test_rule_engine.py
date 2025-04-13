# tests/test_email_organizer/test_rule_engine.py
import unittest
import os
import json
from modules.email_organizer.rule_engine import RuleEngine

class TestRuleEngine(unittest.TestCase):

    def setUp(self):
        self.rules_json_data = {
            "rules": [
                {
                    "id": "rule1",
                    "description": "Move important job portal emails",
                    "priority": 1,
                    "condition_logic": "AND",
                    "conditions": [
                        {"field": "subject", "operation": "contains", "value": "Job Alert"},
                        {"field": "from", "operation": "ends_with", "value": "@jobportal.com"}
                    ],
                    "action": {"type": "move_to_folder", "target": "JobAlerts"}
                },
                {
                    "id": "rule2",
                    "description": "Mark promotional emails or from specific senders",
                    "priority": 2,
                    "condition_logic": "OR",
                    "conditions": [
                        {"field": "subject", "operation": "contains", "value": "Sale"},
                        {"field": "from", "operation": "starts_with", "value": "promotions@"},
                        {"field": "from", "operation": "in", "value": ["newsletter@companyA.com", "offers@companyB.net"]}
                    ],
                    "action": {"type": "add_category", "category_name": "Promotional"}
                },
                {
                    "id": "rule3",
                    "description": "Use AI scoring for urgent-sounding emails and mark as suspicious",
                    "priority": 5,
                    "condition_logic": "AND",
                    "conditions": [
                        {"field": "subject", "operation": "matches_regex", "value": ".*(urgent|important|critical).*"}
                    ],
                    "action": {"type": "mark_as_suspicious", "use_scoring_model": True}
                },
                {
                    "id": "rule4",
                    "description": "Delete very large emails",
                    "priority": 6,
                    "condition_logic": "AND",
                    "conditions": [
                        {"field": "size", "operation": "greater_than", "value": 1000000}
                    ],
                    "action": {"type": "delete"}
                },
                {
                    "id": "rule5",
                    "description": "Stop processing for emails from known contacts",
                    "priority": 0,
                    "condition_logic": "OR",
                    "conditions": [
                        {"field": "from", "operation": "contains", "value": "friend@example.com"},
                        {"field": "from", "operation": "contains", "value": "family@example.com"}
                    ],
                    "action": {"type": "stop_processing"}
                },
                {
                    "id": "rule6",
                    "description": "Mark as read if subject is just 'Hello'",
                    "priority": 3,
                    "condition_logic": "AND",
                    "conditions": [
                        {"field": "subject", "operation": "equals_ignore_case", "value": "hello"}
                    ],
                    "action": {"type": "mark_as_read"}
                },
                {
                    "id": "rule7",
                    "description": "Flag emails with no subject",
                    "priority": 4,
                    "condition_logic": "AND",
                    "conditions": [
                        {"field": "subject", "operation": "is_empty", "value": None}
                    ],
                    "action": {"type": "add_flag", "flag_type": "no_subject"}
                },
                {
                    "id": "rule8",
                    "description": "Remove flag if email is not from a specific domain",
                    "priority": 7,
                    "condition_logic": "AND",
                    "conditions": [
                        {"field": "from", "operation": "not_contains", "value": "@trusted-domain.com"}
                    ],
                    "action": {"type": "remove_flag", "flag_type": "important"}
                },
                {
                    "id": "rule9",
                    "description": "Forward important attachments",
                    "priority": 8,
                    "condition_logic": "AND",
                    "conditions": [
                        {"field": "has_attachments", "operation": "equals", "value": True},
                        {"field": "attachment_name", "operation": "contains", "value": "report.pdf"}
                    ],
                    "action": {"type": "forward_to", "target_email": "reports@example.com"}
                },
                {
                    "id": "rule10",
                    "description": "Reply to specific sender",
                    "priority": 9,
                    "condition_logic": "AND",
                    "conditions": [
                        {"field": "from", "operation": "equals", "value": "support@example.com"},
                        {"field": "subject", "operation": "startswith", "value": "Ticket #"}
                    ],
                    "action": {"type": "reply_with_template", "template_id": "support_reply"}
                },
                {
                    "id": "rule11",
                    "description": "Set high importance for VIP senders",
                    "priority": 0.5,
                    "condition_logic": "OR",
                    "conditions": [
                        {"field": "from", "operation": "in", "value": ["ceo@example.com", "president@example.com"]}
                    ],
                    "action": {"type": "set_importance", "level": "high"}
                },
                {
                    "id": "rule12",
                    "description": "Add 'Finance' category for invoices",
                    "priority": 3.5,
                    "condition_logic": "AND",
                    "conditions": [
                        {"field": "subject", "operation": "contains", "value": "Invoice"}
                    ],
                    "action": {"type": "add_category", "category_name": "Finance"}
                },
                {
                    "id": "rule13",
                    "description": "Mark as unread if it's a reminder",
                    "priority": 6.5,
                    "condition_logic": "AND",
                    "conditions": [
                        {"field": "subject", "operation": "contains", "value": "Reminder"}
                    ],
                    "action": {"type": "mark_as_unread"}
                },
                {
                    "id": "rule14",
                    "description": "Check if body is not empty",
                    "priority": 7.5,
                    "condition_logic": "AND",
                    "conditions": [
                        {"field": "body", "operation": "is_not_empty", "value": None}
                    ],
                    "action": {"type": "no_op"} # Dummy action for testing condition
                },
                {
                    "id": "rule15",
                    "description": "Check if subject is not in a list",
                    "priority": 8.5,
                    "condition_logic": "AND",
                    "conditions": [
                        {"field": "subject", "operation": "not_in", "value": ["FWD:", "RE:"]}
                    ],
                    "action": {"type": "no_op"} # Dummy action for testing condition
                }
            ]
        }
        self.rule_engine = RuleEngine(self.rules_json_data)

    # Test case for the 'not_contains' operator
    def test_condition_operator_not_contains(self):
        email = {"subject": "Important Announcement", "from": "user@trusted-domain.com"}
        actions = self.rule_engine.evaluate(email)
        self.assertNotIn({"type": "remove_flag", "flag_type": "important"}, actions)

        email_trigger = {"subject": "Important Announcement", "from": "spam@example.com"}
        actions_trigger = self.rule_engine.evaluate(email_trigger)
        self.assertIn({"type": "remove_flag", "flag_type": "important"}, actions_trigger) # Add a test where it should be found
    # Test case for the 'startswith' operator
    def test_condition_operator_startswith(self):
        email = {"subject": "Ticket #12345: Issue reported", "from": "support@example.com"}
        actions = self.rule_engine.evaluate(email)
        self.assertIn({"type": "reply_with_template", "template_id": "support_reply"}, actions)

        email_no_match = {"subject": "Re: Ticket #12345", "from": "support@example.com"}
        actions_no_match = self.rule_engine.evaluate(email_no_match)
        self.assertNotIn({"type": "reply_with_template", "template_id": "support_reply"}, actions_no_match)

    # Test case for the 'endswith' operator
    def test_condition_operator_endswith(self):
        email = {"subject": "Quarterly report.pdf", "has_attachments": True, "attachment_name": "Quarterly report.pdf"}
        actions = self.rule_engine.evaluate(email)
        self.assertIn({"type": "forward_to", "target_email": "reports@example.com"}, actions)

        email_no_match = {"subject": "Quarterly report.txt", "has_attachments": True, "attachment_name": "Quarterly report.txt"}
        actions_no_match = self.rule_engine.evaluate(email_no_match)
        self.assertNotIn({"type": "forward_to", "target_email": "reports@example.com"}, actions_no_match)

    # Test case for the 'matches_regex' operator
    def test_condition_operator_matches_regex(self):
        email = {"subject": "This is an urgent matter!"}
        actions = self.rule_engine.evaluate(email)
        self.assertIn({"type": "mark_as_suspicious", "use_scoring_model": True}, actions)

        email_no_match = {"subject": "Important info"}
        actions_no_match = self.rule_engine.evaluate(email_no_match)
        self.assertNotIn({"type": "mark_as_suspicious", "use_scoring_model": True}, actions_no_match)

    # Test case for the 'equals_ignore_case' operator
    def test_condition_operator_equals_ignore_case(self):
        email_lower = {"subject": "hello"}
        actions_lower = self.rule_engine.evaluate(email_lower)
        self.assertIn({"type": "mark_as_read"}, actions_lower)

        email_upper = {"subject": "HELLO"}
        actions_upper = self.rule_engine.evaluate(email_upper)
        self.assertIn({"type": "mark_as_read"}, actions_upper)

        email_mixed = {"subject": "Hello"}
        actions_mixed = self.rule_engine.evaluate(email_mixed)
        self.assertIn({"type": "mark_as_read"}, actions_mixed)

        email_no_match = {"subject": "Hi"}
        actions_no_match = self.rule_engine.evaluate(email_no_match)
        self.assertNotIn({"type": "mark_as_read"}, actions_no_match)

    # Test case for the 'greater_than' operator
    def test_condition_operator_greater_than(self):
        email_large = {"size": 1500000}
        actions_large = self.rule_engine.evaluate(email_large)
        self.assertIn({"type": "delete"}, actions_large)

        email_small = {"size": 500000}
        actions_small = self.rule_engine.evaluate(email_small)
        self.assertNotIn({"type": "delete"}, actions_small)

    # Test case for the 'less_than' operator
    def test_condition_operator_less_than(self):
        # Assuming a rule to test 'less_than' exists (no direct one in default)
        self.rule_engine.rules.append({
            "id": "temp_rule_lt",
            "priority": 100,
            "condition_logic": "AND",
            "conditions": [{"field": "size", "operation": "less_than", "value": 600000}],
            "action": {"type": "mark_as_unread"}
        })
        email_small = {"size": 500000}
        actions_small = self.rule_engine.evaluate(email_small)
        self.assertIn({"type": "mark_as_unread"}, actions_small)
        self.rule_engine.rules.pop() # Clean up

        email_large = {"size": 1500000}
        actions_large = self.rule_engine.evaluate(email_large)
        self.assertNotIn({"type": "mark_as_unread"}, actions_large)

    # Test case for the 'greater_than_or_equal' operator
    def test_condition_operator_greater_than_or_equal(self):
        self.rule_engine.rules.append({
            "id": "temp_rule_gte",
            "priority": 100,
            "condition_logic": "AND",
            "conditions": [{"field": "size", "operation": "greater_than_or_equal", "value": 1500000}],
            "action": {"type": "add_flag", "flag_type": "large"}
        })
        email_equal = {"size": 1500000}
        actions_equal = self.rule_engine.evaluate(email_equal)
        self.assertIn({"type": "add_flag", "flag_type": "large"}, actions_equal)
        email_greater = {"size": 2000000}
        actions_greater = self.rule_engine.evaluate(email_greater)
        self.assertIn({"type": "add_flag", "flag_type": "large"}, actions_greater)
        self.rule_engine.rules.pop() # Clean up

    # Test case for the 'less_than_or_equal' operator
    def test_condition_operator_less_than_or_equal(self):
        self.rule_engine.rules.append({
            "id": "temp_rule_lte",
            "priority": 100,
            "condition_logic": "AND",
            "conditions": [{"field": "size", "operation": "less_than_or_equal", "value": 500000}],
            "action": {"type": "add_category", "category_name": "small"}
        })
        email_equal = {"size": 500000}
        actions_equal = self.rule_engine.evaluate(email_equal)
        self.assertIn({"type": "add_category", "category_name": "small"}, actions_equal)
        email_less = {"size": 300000}
        actions_less = self.rule_engine.evaluate(email_less)
        self.assertIn({"type": "add_category", "category_name": "small"}, actions_less)
        self.rule_engine.rules.pop() # Clean up

    # Test case for the 'is_empty' operator
    def test_condition_operator_is_empty(self):
        email_empty = {"subject": None}
        actions_empty = self.rule_engine.evaluate(email_empty)
        self.assertIn({"type": "add_flag", "flag_type": "no_subject"}, actions_empty)

        email_not_empty = {"subject": "Hello"}
        actions_not_empty = self.rule_engine.evaluate(email_not_empty)
        self.assertNotIn({"type": "add_flag", "flag_type": "no_subject"}, actions_not_empty)

    # Test case for the 'is_not_empty' operator
    def test_condition_operator_is_not_empty(self):
        email_not_empty_body = {"body": "This is the email body."}
        actions_not_empty_body = self.rule_engine.evaluate(email_not_empty_body)
        self.assertTrue(any(action.get("type") == "no_op" for action in actions_not_empty_body))

        email_empty_body = {"body": None}
        actions_empty_body = self.rule_engine.evaluate(email_empty_body)
        self.assertFalse(any(action.get("type") == "no_op" for action in actions_empty_body))

    # Test case for the 'in' operator
    def test_condition_operator_in(self):
        email_match = {"from": "newsletter@companyA.com"}
        actions_match = self.rule_engine.evaluate(email_match)
        self.assertIn({"type": "add_category", "category_name": "Promotional"}, actions_match)

        email_no_match = {"from": "other@example.com"}
        actions_no_match = self.rule_engine.evaluate(email_no_match)
        self.assertNotIn({"type": "add_category", "category_name": "Promotional"}, actions_no_match)

    # Test case for the 'not_in' operator
    def test_condition_operator_not_in(self):
        # Test case where the subject IS in the list, so 'no_op' should NOT be triggered
        email_match_in = {"subject": "FWD:"}
        actions_match_in = self.rule_engine.evaluate(email_match_in)
        self.assertFalse(any(action.get("type") == "no_op" for action in actions_match_in), f"Unexpected 'no_op' action: {actions_match_in}")

        email_match_in_re = {"subject": "RE:"}
        actions_match_in_re = self.rule_engine.evaluate(email_match_in_re)
        self.assertFalse(any(action.get("type") == "no_op" for action in actions_match_in_re), f"Unexpected 'no_op' action: {actions_match_in_re}")

        # Test case where the subject is NOT in the list, so 'no_op' SHOULD be triggered
        email_no_match = {"subject": "Urgent Email"}
        actions_no_match = self.rule_engine.evaluate(email_no_match)
        self.assertTrue(any(action.get("type") == "no_op" for action in actions_no_match), f"Expected 'no_op' action not found: {actions_no_match}")

        email_no_match_partial = {"subject": "FWD: Important"}
        actions_no_match_partial = self.rule_engine.evaluate(email_no_match_partial)
        self.assertTrue(any(action.get("type") == "no_op" for action in actions_no_match_partial), f"Expected 'no_op' action not found: {actions_no_match_partial}")