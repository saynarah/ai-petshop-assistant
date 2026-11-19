
import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

from langsmith import Client, traceable


@traceable(
    name="PetShop Test",
    run_type="chain"
)
def test_trace():
    return {
        "message": "Hello from AI Pet Shop Assistant",
        "status": "success"
    }


if __name__ == "__main__":
    print("Tracing:", os.getenv("LANGSMITH_TRACING"))
    print("Project:", os.getenv("LANGSMITH_PROJECT"))

    result = test_trace()

    print("Result:", result)

    client = Client()
    client.flush()

    print("Trace submission attempted.")
