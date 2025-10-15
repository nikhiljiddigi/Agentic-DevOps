import argparse

from pr_reviewer.agent import run_pr_agent
from predeploy_config_gate.agent import run_config_agent
from security_vulnerability_watcher.agent import run_security_agent
from cicd_failure_explainer.agent import run_cicd_agent
from infra_anamoly_explainer.agent import run_anomaly_agent
from incident_rca_generator.agent import run_rca_agent


def main():
    parser = argparse.ArgumentParser(description="Agentic DevSecOps Flow")
    parser.add_argument(
        "--stage",
        choices=["pr", "build", "post"],
        required=True,
        help="Choose stage to execute: pr | build | post",
    )
    args = parser.parse_args()

    if args.stage == "pr":
        run_pr_agent()
        print("\n----------------------------------------")
        run_config_agent()
        print("\n----------------------------------------")
        run_security_agent()

    elif args.stage == "build":
        run_cicd_agent()

    elif args.stage == "post":
        run_anomaly_agent()
        run_rca_agent()


if __name__ == "__main__":
    main()
