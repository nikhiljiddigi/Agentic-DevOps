import asyncio
from agent import AgenticInfraRCA

def main():
    print("🚀 Starting entity-agnostic Agentic Infra RCA ...")
    agent = AgenticInfraRCA()
    # default: analyze Pod, Node, Deployment, Service
    asyncio.run(agent.analyze_cluster(exclude_system=True))

if __name__ == "__main__":
    main()
