from behave import given, when, then
import credit_decision_pb2
from app import CreditDecisionServicer

@given("an applicant with high income and good credit history")
def step_good_credit(context):
    context.request = credit_decision_pb2.CreditDecisionRequest(
            applicant_id="1001",
            income=90000,
            loan_amount=100000,
            credit_history=40,
            delinquencies=0
    )

@given("an applicant with low credit score and many delinquencies")
def step_bad_credit(context):
    context.request = credit_decision_pb2.CreditDecisionRequest(
            applicant_id="1002",
            income=30000,
            loan_amount=100000,
            credit_history=5,
    )

@when("the application is evaluated")
def step_evaluate(context):
    context.response = CreditDecisionServicer().EvaluateApplication(context.request, None)

@then("the decision should be approved with a low interest rate")
def step_approved(context):
    assert context.response.status == "approved"
    assert context.response.interest_rate < 0.12

@then("the decision should be rejected due to high risk")
def step_rejected(context):
    assert context.response.status == "rejected"
    assert "risk" in context.response.reason.lower()