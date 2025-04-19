from concurrent import futures
import grpc
import credit_decision_pb2
import credit_decision_pb2_grpc
import requests
import logging
import time
import os
from dotenv import load_dotenv

# Only load .env.local when not running in Docker
if os.getenv("DOCKER_ENV") != "true":
    load_dotenv(dotenv_path=".env.local")

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class CreditDecisionServicer(credit_decision_pb2_grpc.CreditDecisionServiceServicer):
    def EvaluateApplication(self, request, context):
        logger.info(f"creditdecisionservice - Received application for evaluation")
        applicant_info = {
            'applicant_id': request.applicant_id,
            'income': request.income,
            'loan_amount': request.loan_amount,
            'credit_history': request.credit_history,
            'delinquencies': request.delinquencies,
        }

        logger.info(f" Performing Risk Scoring for applicant ID: {applicant_info['applicant_id']}")
        start_time = time.time()
        RSE_HOST = os.getenv("RISKSCORINGENGINE_HOST", "localhost:5003")
        risk_score = requests.post(f"http://{RSE_HOST}/risk-score", json={"applicant_info": applicant_info}).json()["risk_score"]
        # risk_score = requests.post("http://risk-scoring-engine:5003/risk-score", json={"applicant_info": applicant_info}).json()["risk_score"]
        # risk_score = requests.post("http://localhost:5003/risk-score", json={"applicant_info": applicant_info}).json()["risk_score"]
        logger.info(f" Risk Scoring took {time.time() - start_time:.2f}s")

        start_time = time.time()
        logger.info(f" Performing Underwriting for applicant ID {applicant_info['applicant_id']} with risk score : {risk_score}")
        UW_HOST = os.getenv("CREDITUNDERWRITING_HOST", "localhost:5004")
        logger.info(f"value of UW_HOST from env : {UW_HOST}")
        underwriting = requests.post(f"http://{UW_HOST}/underwrite", json={"applicant_info": applicant_info, "risk_score": risk_score}).json()
        # underwriting = requests.post("http://credit-underwriting:5004/underwrite", json={"applicant_info": applicant_info, "risk_score": risk_score}).json()
        # underwriting = requests.post("http://localhost:5004/underwrite", json={"applicant_info": applicant_info, "risk_score": risk_score}).json()
        logger.info(f" Underwriting took {time.time() - start_time:.2f}s")

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
    logger.info(" Starting Credit Decision server on port 5005...")
    server.start()
    logger.info(" Credit Decision server started")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()