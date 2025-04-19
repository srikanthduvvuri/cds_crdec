import credit_decision_pb2
from app import CreditDecisionServicer

class MockContext:
    pass

def test_evaluate_application(monkeypatch):
    servicer = CreditDecisionServicer()
    request = credit_decision_pb2.CreditDecisionRequest(
            applicant_id="123",
            income=60000,
            loan_amount=100000,
            credit_history=40,
            delinquencies=0
    )

    monkeypatch.setattr("requests.post", lambda url, json: MockResponse(url))

    result = servicer.EvaluateApplication(request, MockContext())
    assert result.status in ["approved", "rejected"]
    assert isinstance(result.risk_score, int)

class MockResponse:
    def __init__(self, url):
        if "risk-score" in url:
            self._json = {"risk_score": 720}
        else:
            self._json = {
                "status": "approved",
                "interest_rate": 0.1,
                "reason": "Approved with interest rate 0.1"
            }

    def json(self):
        return self._json
