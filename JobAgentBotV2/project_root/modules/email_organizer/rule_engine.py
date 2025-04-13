# modules/email_organizer/rule_engine.py

from typing import List, Dict, Any, Optional
import operator
import re  # For regular expression matching

class RuleEngine:
    """
    A class responsible for evaluating email data against a set of refined rules
    defined in a JSON structure and determining the actions to be taken.
    It supports a wide range of condition operators, logical combinations,
    and action types.
    """
    def __init__(self, rules_json: Dict[str, Any], use_ml_model: bool = False, model: Any = None):
        """
        Initializes the RuleEngine with a JSON structure containing the rules
        and optional ML components.

        Args:
            rules_json (Dict[str, Any]): A dictionary loaded from the JSON rule file.
            use_ml_model (bool, optional): A flag indicating whether to use a machine
                                           learning model for evaluation. Defaults to False.
            model (Any, optional): The loaded machine learning model object. Defaults to None.
        """
        self.rules = rules_json.get("rules", [])
        self.use_ml_model = use_ml_model
        self.model = model
        self.operators = {
            "equals": operator.eq,
            "contains": lambda a, b: b.lower() in a.lower() if isinstance(a, str) and isinstance(b, str) else False,
            "not_contains": lambda a, b: b.lower() not in a.lower() if isinstance(a, str) and isinstance(b, str) else True,
            "startswith": lambda a, b: a.lower().startswith(b.lower()) if isinstance(a, str) and isinstance(b, str) else False,
            "endswith": lambda a, b: a.lower().endswith(b.lower()) if isinstance(a, str) and isinstance(b, str) else False,
            "matches_regex": lambda a, b: re.match(b, a) is not None if isinstance(a, str) and isinstance(b, str) else False,
            "equals_ignore_case": lambda a, b: a.lower() == b.lower() if isinstance(a, str) and isinstance(b, str) else False,
            "greater_than": operator.gt,
            "less_than": operator.lt,
            "greater_than_or_equal": operator.ge,
            "less_than_or_equal": operator.le,
            "is_empty": lambda a, b: not a,  # b is ignored
            "is_not_empty": lambda a, b: bool(a), # b is ignored
            "in": lambda a, b: a.lower() in [item.lower() for item in b] if isinstance(b, list) and isinstance(a, str) else (a in b if isinstance(b, list) else False),
            "not_in": lambda a, b: a.lower() not in [item.lower() for item in b] if isinstance(b, list) and isinstance(a, str) else (a not in b if isinstance(b, list) else True),
            "equals": operator.eq
        }
    def evaluate(self, email_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Evaluates the given email data against the loaded rules and returns a list of actions
        to be taken. Rules are evaluated based on their priority. Actions from all
        matching rules are collected, respecting the 'stop_processing' action.

        Args:
            email_data (Dict[str, Any]): A dictionary containing the email attributes.

        Returns:
            List[Dict[str, Any]]: A list of action dictionaries to be performed on the email,
                                 ordered by the priority of the matching rule.
        """
        matching_actions = []
        stop_processing = False

        for rule in sorted(self.rules, key=lambda r: r.get("priority", 100)):
            if stop_processing:
                break

            if self._evaluate_rule(rule, email_data):
                action = rule.get("action")
                if action:
                    matching_actions.append({
                        "priority": rule.get("priority", 100),
                        "action": action
                    })
                    if action.get("type") == "stop_processing":
                        stop_processing = True

        # Sort actions by priority (lower is higher)
        matching_actions.sort(key=lambda item: item["priority"])

        return [item["action"] for item in matching_actions]

    def _evaluate_rule(self, rule: Dict[str, Any], email_data: Dict[str, Any]) -> bool:
        """
        Evaluates a single rule against the given email data. It checks the conditions
        defined in the rule and returns True if the rule matches, False otherwise,
        based on the specified 'condition_logic'.

        Args:
            rule (Dict[str, Any]): A dictionary representing a single rule.
            email_data (Dict[str, Any]): A dictionary containing the email attributes.

        Returns:
            bool: True if the rule's conditions are met, False otherwise.
        """
        conditions = rule.get("conditions", [])
        logic = rule.get("condition_logic", "AND").upper()

        if not conditions:
            return True

        results = []
        for condition in conditions:
            field = condition.get("field")
            operation = condition.get("operation")
            value = condition.get("value")

            print(f"Evaluating condition: field='{field}', operation='{operation}', value='{value}'")

            if field and operation and field in email_data:
                field_value = email_data[field]
                op_func = self.operators.get(operation)
                if op_func:
                    result = op_func(field_value, value)
                    print(f"  Field Value: '{field_value}', Result: {result}")
                    results.append(result)
                else:
                    print(f"Warning: Unknown operation '{operation}' in rule '{rule.get('id')}'")
                    results.append(False)
            else:
                results.append(False)

        print(f"Condition results: {results}, Logic: {logic}")

        if logic == "AND":
            final_result = all(results)
        elif logic == "OR":
            final_result = any(results)
        else:
            print(f"Warning: Unknown condition logic '{logic}' in rule '{rule.get('id')}'. Assuming AND.")
            final_result = all(results)

        print(f"Final rule result: {final_result}")
        return final_result
    # ML-based scoring would be integrated here within the evaluate method
    # if use_ml_model is True and self.model is available.
    # The logic for how ML scores influence actions would need to be defined.

    def _resolve_conflicts(self, matched_actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        This method is now less about strict conflict resolution and more about
        returning all triggered actions in order of priority, respecting 'stop_processing'.

        Args:
            matched_actions (List[Dict[str, Any]]): A list of action dictionaries
                                                    from matching rules, along with their priorities.

        Returns:
            List[Dict[str, Any]]: A list of action dictionaries sorted by priority.
        """
        # Actions are already sorted by priority in the evaluate method.
        return [item["action"] for item in matched_actions]