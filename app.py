from concurrent import futures
import grpc
import credit_decision_pb2
import credit_decision_pb2_grpc
import requests

class CreditDecisionServicer(credit_decision_pb2_grpc.CreditDecisionServiceServicer):
    def EvaluateApplication(self, request, context):
        print("Received application for evaluation")
        applicant_info = {
            'applicant_id': request.applicant_id,
            'income': request.income,
            'loan_amount': request.loan_amount,
            'credit_history': request.credit_history,
            'delinquencies': request.delinquencies,
        }

        print(f" Performing Risk Scoring for applicant ID: {applicant_info['applicant_id']}")
        risk_score = requests.post("http://risk-scoring-engine:5003/risk-score", json={"applicant_info": applicant_info}).json()["risk_score"]
        # risk_score = requests.post("http://localhost:5003/risk-score", json={"applicant_info": applicant_info}).json()["risk_score"]
        print(f" Performing Underwriting for applicant ID {applicant_info['applicant_id']} with risk score : {risk_score}")
        underwriting = requests.post("http://credit-underwriting:5004/underwrite", json={"applicant_info": applicant_info, "risk_score": risk_score}).json()
        # underwriting = requests.post("http://localhost:5004/underwrite", json={"applicant_info": applicant_info, "risk_score": risk_score}).json()

        return credit_decision_pb2.CreditDecision(
            status=underwriting["status"],
            interest_rate=underwriting.get("interest_rate", 0.0),
            reason=underwriting["reason"],
            risk_score=risk_score
        )
    

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    credit_decision_pb2_grpc.add_CreditDecisionServiceServicer_to_server(CreditDecisionServicer(), server)
    server.add_insecure_port('[::]:5005')
    print(" Starting Credit Decision server on port 5005...")
    server.start()
    print(" Credit Decision server started")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()