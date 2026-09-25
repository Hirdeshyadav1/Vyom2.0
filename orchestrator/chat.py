from orchestrator import VyomOrchestrator
from security_brain import UserLevel

print("=== Vyom se baat karo ===")
print("Rukne ke liye 'exit' likho.\n")

o = VyomOrchestrator(mode='gemini')

while True:
    msg = input('Tum: ')
    if msg.strip().lower() == 'exit':
        print('Vyom: Alvida!')
        break
    if not msg.strip():
        continue
    response = o.handle_message('u1', UserLevel.TRUSTED, msg)
    print('Vyom:', response)
    print()
