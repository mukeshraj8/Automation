# tests/test_email_organizer/test_rule_engine.py
import unittest
import os
import json
from modules.email_organizer.rule_engine import RuleEngine

class TestRuleEngine(unittest.TestCase):

    def setUp(self):
        # Define the path for our rules config file
        self.config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'email_rules_config.json')

        # Ensure the directory exists
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)

        # Ensure the file exists with initial mock data
        self.mock_rules_data = {
            "rules": [
                {
                    "name": "Spam Filter",
                    "conditions": [
                        {"field": "sender", "operation": "equals", "value": "spam@domain.com"},
                        {"field": "subject", "operation": "contains", "value": "free money"}
                    ],
                    "action": "move_to_spam",
                    "priority": 1
                },
                {
                    "name": "Important Email",
                    "conditions": [
                        {"field": "sender", "operation": "equals", "value": "important@domain.com"}
                    ],
                    "action": "move_to_important",
                    "priority": 2
                }
            ]
        }

        # Write mock data to the config file for testing
        with open(self.config_path, 'w') as f:
            json.dump(self.mock_rules_data, f, indent=4)

        # Initialize RuleEngine (Assuming it loads rules from the provided list)
        self.rule_engine = RuleEngine(rules=self.mock_rules_data.get("rules", []))

    def tearDown(self):
        # Clean up the mock rules config after tests
        if os.path.exists(self.config_path):
            os.remove(self.config_path)
            # Optionally remove the directory if it was created solely for testing
            if not os.listdir(os.path.dirname(self.config_path)):
                os.rmdir(os.path.dirname(self.config_path))

    def test_valid_rule_parsing(self):
        # Test that rules are correctly loaded during initialization
        rules = self.rule_engine.rules
        self.assertEqual(len(rules), 2)  # We have two rules in our mock config
        self.assertEqual(rules[0]['name'], 'Spam Filter')
        self.assertEqual(rules[1]['name'], 'Important Email')

    def test_multiple_conditions_handling_and_logic(self):
        # Test that multiple conditions inside a rule are handled correctly with AND logic (default)
        email_data_spam = {"sender": "spam@domain.com", "subject": "Get free money now!"}
        actions_spam = self.rule_engine.evaluate(email_data_spam)
        self.assertIn("move_to_spam", actions_spam)

        email_data_not_spam = {"sender": "notspam@domain.com", "subject": "free money"}
        actions_not_spam = self.rule_engine.evaluate(email_data_not_spam)
        self.assertEqual(len(actions_not_spam), 0)

        # Add a rule with OR logic for testing
        self.rule_engine.rules.append({
            "name": "Promotional or Urgent",
            "logic": "OR",
            "conditions": [
                {"field": "subject", "operation": "contains", "value": "discount"},
                {"field": "subject", "operation": "contains", "value": "urgent"}
            ],
            "action": "flag_promotional_urgent",
            "priority": 3
        })
        email_data_promo = {"sender": "info@example.com", "subject": "Limited time discount!"}
        actions_promo = self.rule_engine.evaluate(email_data_promo)
        self.assertIn("flag_promotional_urgent", actions_promo)

        email_data_urgent = {"sender": "support@example.com", "subject": "Urgent: Account issue"}
        actions_urgent = self.rule_engine.evaluate(email_data_urgent)
        self.assertIn("flag_promotional_urgent", actions_urgent)

        email_data_neither = {"sender": "friend@example.com", "subject": "Catching up"}
        actions_neither = self.rule_engine.evaluate(email_data_neither)
        self.assertEqual(len(actions_neither), 0)

    def test_priority_handling(self):
        # Test that the priority attribute is respected in action selection
        email_data_both_match = {"sender": "spam@domain.com", "subject": "Important: Get free money now!"}
        actions = self.rule_engine.evaluate(email_data_both_match)
        # Assuming lower priority number means higher priority, "Spam Filter" should take precedence
        self.assertIn("move_to_spam", actions)
        self.assertNotIn("move_to_important", actions)

    def test_conflict_resolution(self):
        # Test conflict resolution by ensuring only the highest priority action is returned
        self.rule_engine.rules.append({
            "name": "Conflicting Rule",
            "conditions": [{"field": "subject", "operation": "contains", "value": "money"}],
            "action": "archive",
            "priority": 0  # Higher priority than "Spam Filter"
        })
        email_data_conflict = {"sender": "some@domain.com", "subject": "Get money fast!"}
        actions = self.rule_engine.evaluate(email_data_conflict)
        self.assertIn("archive", actions)
        self.assertNotIn("move_to_spam", actions)

    def test_condition_operators(self):
        # Test different condition operators
        self.rule_engine.rules.extend([
            {"name": "StartsWith Test", "conditions": [{"field": "subject", "operation": "startswith", "value": "Meeting"}], "action": "move_to_meetings", "priority": 4},
            {"name": "EndsWith Test", "conditions": [{"field": "subject", "operation": "endswith", "value": ".pdf"}], "action": "move_to_pdfs", "priority": 5},
            {"name": "GreaterThan Test", "conditions": [{"field": "size", "operation": "greater_than", "value": 1000}], "action": "flag_large", "priority": 6},
            {"name": "LessThan Test", "conditions": [{"field": "size", "operation": "less_than", "value": 500}], "action": "move_to_small", "priority": 7},
        ])

        self.assertEqual(self.rule_engine.evaluate({"subject": "Meeting at 3 PM"}), ["move_to_meetings"])
        self.assertEqual(self.rule_engine.evaluate({"subject": "Report.pdf"}), ["move_to_pdfs"])
        self.assertEqual(self.rule_engine.evaluate({"size": 1500}), ["flag_large"])
        self.assertEqual(self.rule_engine.evaluate({"size": 300}), ["move_to_small"])
        self.assertEqual(self.rule_engine.evaluate({"size": 750}), [])

    def test_no_matching_rule(self):
        # Test the case where no rules match the email
        email_data = {"sender": "unknown@domain.com", "subject": "Just a regular email"}
        actions = self.rule_engine.evaluate(email_data)
        self.assertEqual(len(actions), 0)

    def test_rule_without_action(self):
        # Test a rule that matches but has no action defined
        self.rule_engine.rules.append({
            "name": "Match but No Action",
            "conditions": [{"field": "subject", "operation": "contains", "value": "info"}],
            "priority": 8
        })
        email_data = {"sender": "test@example.com", "subject": "Information needed"}
        actions = self.rule_engine.evaluate(email_data)
        self.assertEqual(len(actions), 0)


if __name__ == '__main__':
    unittest.main()