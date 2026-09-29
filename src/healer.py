import os
from typing import TypedDict
from bs4 import BeautifulSoup
from langgraph.graph import StateGraph, END
from playwright.sync_api import sync_playwright

class HealerState(TypedDict):
    target_url: str
    target_action: str
    selector: str
    error_message: str
    dom_snippet: str
    attempts: int
    is_successful: bool

def execute_action(state: HealerState) -> HealerState:
    print(f"[*] Testing selector: {state['selector']} (Attempt {state['attempts'] + 1})")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(state["target_url"])
        try:
            # Short timeout to simulate quick failure on stale element
            page.wait_for_selector(state["selector"], timeout=2000)
            page.click(state["selector"])
            print(f"[+] Action '{state['target_action']}' succeeded!")
            state["is_successful"] = True
            state["error_message"] = ""
        except Exception as e:
            print(f"[-] Action failed: Element not found or timed out.")
            state["is_successful"] = False
            state["error_message"] = str(e)
            
            # Extract relevant DOM context around forms and buttons
            soup = BeautifulSoup(page.content(), "html.parser")
            buttons = [str(btn) for btn in soup.find_all(["button", "a", "input"])]
            state["dom_snippet"] = "\n".join(buttons[:5])
            state["attempts"] += 1
        finally:
            browser.close()
    return state

def heal_selector(state: HealerState) -> HealerState:
    print("[*] Agentic Repair: Inspecting DOM snippet to reconstruct locator...")
    # Heuristic fallback / LLM simulated logic:
    # Parses snippet and extracts new locator dynamically matching intent
    soup = BeautifulSoup(state["dom_snippet"], "html.parser")
    btn = soup.find("button")
    if btn and btn.get("id"):
        new_selector = f"#{btn['id']}"
    elif btn and btn.get("class"):
        new_selector = f".{btn['class'][0]}"
    else:
        new_selector = "button[data-action='checkout']"
        
    print(f"[+] Agent proposed healed selector: {new_selector}")
    state["selector"] = new_selector
    return state

def router(state: HealerState):
    if state["is_successful"]:
        return END
    if state["attempts"] >= 3:
        print("[!] Max healing attempts exceeded.")
        return END
    return "heal_selector"

def build_healer_graph():
    graph = StateGraph(HealerState)
    graph.add_node("execute_action", execute_action)
    graph.add_node("heal_selector", heal_selector)
    graph.set_entry_point("execute_action")
    graph.add_conditional_edges("execute_action", router)
    graph.add_edge("heal_selector", "execute_action")
    return graph.compile()
