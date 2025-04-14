Feature: Credit Decision
  Scenario: Approve applicant with strong financials
    Given an applicant with high income and good credit history
    When the application is evaluated
    Then the decision should be approved with a low interest rate

  Scenario: Reject applicant with poor credit history
    Given an applicant with low credit score and many delinquencies
    When the application is evaluated
    Then the decision should be rejected due to high risk