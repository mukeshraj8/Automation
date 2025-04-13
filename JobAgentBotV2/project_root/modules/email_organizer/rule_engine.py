# modules/email_organizer/rule_engine.py

from typing import List, Dict, Any, Optional
import operator

class RuleEngine:
    """
    A class responsible for evaluating email data against a set of defined rules
    and determining the actions to be taken based on those rules.
    It supports rule-based matching with various operators and an optional
    integration with a machine learning model for additional scoring.
    """
    def __init__(self, rules: List[Dict[str, Any]], use_ml_model: bool = False, model: Any = None):
        """
        Initializes the RuleEngine with a list of rules and optional ML components.

        Args:
            rules (List[Dict[str, Any]]): A list of dictionaries, where each dictionary
                                        represents a rule. Each rule should contain:
                                        - 'conditions' (List[Dict]): A list of conditions to evaluate.
                                        - 'action' (Any): The action to take if the rule matches.
                                        - 'priority' (int, optional): The priority of the rule (lower is higher).
                                        - 'logic' (str, optional): The logical operator ('AND' or 'OR')
                                          to combine conditions. Defaults to 'AND'.
                                        - Optionally, 'field', 'operation', 'value' for simpler rules.
            use_ml_model (bool, optional): A flag indicating whether to use a machine
                                           learning model for evaluation. Defaults to False.
            model (Any, optional): The loaded machine learning model object. Defaults to None.
        """
        self.rules = rules
        self.use_ml_model = use_ml_model
        self.model = model
        self.operators = {
            "equals": operator.eq,
            "contains": lambda a, b: b.lower() in a.lower() if isinstance(a, str) else False,
            "startswith": lambda a, b: a.lower().startswith(b.lower()) if isinstance(a, str) else False,
            "endswith": lambda a, b: a.lower().endswith(b.lower()) if isinstance(a, str) else False,
            "greater_than": operator.gt,
            "less_than": operator.lt
        }

    def evaluate(self, email_data: Dict[str, Any]) -> List[str]:
        """
        Evaluates the given email data against the loaded rules and returns a list of actions
        to be taken. Rules are evaluated based on their priority. In case of multiple
        matching rules, the actions from the rule(s) with the highest priority are returned.

        Args:
            email_data (Dict[str, Any]): A dictionary containing the email attributes
                                        (e.g., 'sender', 'subject', 'body', 'size').

        Returns:
            List[str]: A list of actions to be performed on the email, based on the
                       highest priority matching rule(s).
        """
        matched_actions = []
        scored_results = []

        # --- Rule-based matching ---
        for rule in sorted(self.rules, key=lambda r: r.get("priority", 100)):
            if self._evaluate_rule(rule, email_data):
                action = rule.get("action")
                if action:
                    matched_actions.append((rule.get("priority", 100), action))

        # --- ML-based scoring (optional) ---
        if self.use_ml_model and self.model:
            label, score = self.model.predict(email_data)
            scored_results.append((label, score))

        final_actions = self._resolve_conflicts(matched_actions)
        return final_actions

    def _evaluate_rule(self, rule: Dict[str, Any], email_data: Dict[str, Any]) -> bool:
        """
        Evaluates a single rule against the given email data. It checks the conditions
        defined in the rule and returns True if the rule matches, False otherwise.
        It supports both a list of conditions with a logical operator ('AND'/'OR')
        and a simpler structure with 'field', 'operation', and 'value' directly in the rule.

        Args:
            rule (Dict[str, Any]): A dictionary representing a single rule.
            email_data (Dict[str, Any]): A dictionary containing the email attributes.

        Returns:
            bool: True if the rule's conditions are met, False otherwise.
        """
        conditions = rule.get("conditions")
        logic = rule.get("logic", "AND").upper()

        if not conditions:
            # Fallback for simple rule structure
            conditions = [{
                "field": rule.get("field"),
                "operation": rule.get("operation"),
                "value": rule.get("value")
            }]

        results = []
        for cond in conditions:
            field = cond.get("field")
            operation = cond.get("operation")
            value = cond.get("value")

            field_value = email_data.get(field)
            op_func = self.operators.get(operation)

            if op_func and field_value is not None:
                result = op_func(field_value, value)
                results.append(result)
            else:
                results.append(False)

        if logic == "AND":
            return all(results)
        elif logic == "OR":
            return any(results)
        else:
            return False

    def _resolve_conflicts(self, matched_actions: List[tuple]) -> List[str]:
        """
        Resolves conflicts between multiple matching rules by selecting the action(s)
        from the rule(s) with the highest priority (lowest priority number).

        Args:
            matched_actions (List[tuple]): A list of tuples, where each tuple contains
                                            (priority, action) of a matching rule.

        Returns:
            List[str]: A list of the actions from the highest priority matching rule(s).
                       If no rules matched, an empty list is returned.
        """
        if not matched_actions:
            return []

        matched_actions.sort()  # Sort by priority (ascending)
        highest_priority = matched_actions[0][0]
        final_actions = [action for prio, action in matched_actions if prio == highest_priority]
        return final_actions