"""
Program 22 — Live CEO WhatsApp Interactive CLI Console.

Simulates real-time WhatsApp conversation between CEO and the AI HR Operating System.
Sends messages to http://127.0.0.1:8000/api/v1/integrations/whatsapp/webhook.
"""
import sys, os, httpx, json

sys.stdout.reconfigure(encoding='utf-8')

GREEN  = "\033[92m"
BLUE   = "\033[94m"
YELLOW = "\033[93m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

CEO_PHONE = os.getenv("CEO_PHONE_NUMBER", "+919372267957")

def main():
    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD} 📱 CEO WHATSAPP → AI HRMS INTERACTIVE TERMINAL CONSOLE{RESET}")
    print(f" CEO Phone Number : {GREEN}{CEO_PHONE}{RESET}")
    print(f" Backend Endpoint: {BLUE}http://127.0.0.1:8000/api/v1/integrations/whatsapp/webhook{RESET}")
    print(f"{BOLD}{'='*60}{RESET}")
    print("Type your HR commands (e.g. 'Good morning', 'Hire a Python Lead', 'Approve', 'Show candidates').")
    print("Type 'exit' or 'quit' to end session.\n")

    client = httpx.Client(timeout=45.0)

    while True:
        try:
            user_input = input(f"{BOLD}{GREEN}CEO WhatsApp [{CEO_PHONE}] > {RESET}").strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit"):
                print("Ending WhatsApp session. Goodbye!")
                break

            payload = {
                "From": CEO_PHONE,
                "To": "+14155238886",
                "Body": user_input,
                "MessageSid": "WA_CLI_SIM"
            }

            resp = client.post("http://127.0.0.1:8000/api/v1/integrations/whatsapp/webhook", json=payload)
            if resp.status_code == 200:
                data = resp.json()
                reply = data.get("response_text", "")
                print(f"\n{BOLD}{BLUE}🤖 HRMS AI Agent Response:{RESET}")
                print(f"{reply}\n")
            else:
                print(f"\n{YELLOW}Error {resp.status_code}: {resp.text}{RESET}\n")

        except KeyboardInterrupt:
            print("\nSession ended.")
            break
        except Exception as e:
            print(f"\n{YELLOW}Connection error: {e}{RESET}\n")

if __name__ == "__main__":
    main()
