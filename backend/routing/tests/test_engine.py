from dataclasses import replace

from django.test import SimpleTestCase

from cases.models import ServiceRequest
from routing.engine import Candidate, normalize_text, select_decision


class RoutingEngineTests(SimpleTestCase):
    rule = Candidate(1, "Wireless", 7, 11, 3, (("wi fi", 3), ("network", 2)))

    def test_case_punctuation_whitespace_and_repetition(self):
        result = select_decision("WI-Fi! Wi   Fi", "Network; NETWORK...", [self.rule])
        self.assertEqual(normalize_text("  WI-Fi!  "), "wi fi")
        self.assertEqual((result.rule_id, result.service_id, result.team_id, result.score), (1, 7, 11, 5))
        self.assertEqual(result.status, ServiceRequest.Status.QUEUED)

    def test_repetition_cannot_reach_minimum_score(self):
        result = select_decision("Network, network", "network", [self.rule])
        self.assertIsNone(result.rule_id)
        self.assertEqual(result.status, ServiceRequest.Status.PENDING_TRIAGE)

    def test_partial_word_and_phrase_crossing_fields_do_not_match(self):
        for title, description in [("Networking", "wi finance"), ("wi", "fi")]:
            with self.subTest(title=title):
                result = select_decision(title, description, [replace(self.rule, minimum_score=1)])
                self.assertIsNone(result.rule_id)

    def test_unique_highest_eligible_score_wins_in_either_order(self):
        lower = replace(self.rule, rule_id=2, keywords=(("network", 3),))
        ineligible = replace(self.rule, rule_id=3, minimum_score=20, keywords=(("network", 15),))
        rules = [lower, self.rule, ineligible]
        for order in [rules, reversed(rules)]:
            self.assertEqual(select_decision("wi-fi", "network", order).rule_id, 1)

    def test_equal_highest_scores_do_not_break_ties_even_for_same_service(self):
        result = select_decision("wi-fi", "", [self.rule, replace(self.rule, rule_id=2)])
        self.assertEqual(result.status, ServiceRequest.Status.PENDING_TRIAGE)
        self.assertEqual((result.service_id, result.team_id, result.rule_id, result.score), (None, None, None, 3))
        self.assertIn("Ambiguous", result.reason)

    def test_no_rules(self):
        self.assertIn("No qualifying", select_decision("Help", "Please", []).reason)
