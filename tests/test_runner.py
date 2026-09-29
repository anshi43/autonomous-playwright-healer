import os
import pytest
from src.healer import build_healer_graph

def test_autonomous_healing():
    html_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/mock_page.html"))
    file_url = f"file://{html_path}"

    initial_state = {
        "target_url": file_url,
        "target_action": "Click Place Order",
        "selector": "#submit-btn",  # Broken selector on purpose
        "error_message": "",
        "dom_snippet": "",
        "attempts": 0,
        "is_successful": False
    }

    app = build_healer_graph()
    final_state = app.invoke(initial_state)

    assert final_state["is_successful"] is True
    assert final_state["selector"] == "#submit-btn-v2"
    assert final_state["attempts"] == 1

if __name__ == "__main__":
    pytest.main(["-v", "tests/test_runner.py"])
