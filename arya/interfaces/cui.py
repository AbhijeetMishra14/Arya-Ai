from arya.core.brain import Brain
from arya.modules.voice import VoiceModule

def start_cui():
    print("--------------------------------------------------")
    print("Starting Main Cognitive Core...")
    brain = Brain()
    
    print("Initializing Voice Synthesizer...")
    voice = VoiceModule()
    
    print("\n[SYSTEM]: All Core Modules Online.")
    print("--------------------------------------------------\n")
    
    welcome_msg = "ARYA systems are online. How may I assist you today?"
    print(f"ARYA: {welcome_msg}")
    voice.speak(welcome_msg)
    
    while True:
        try:
            print("\n" + "="*50)
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
                
            words = user_input.lower().replace('.', '').replace(',', '').split()
            exit_commands = {'exit', 'quit', 'bye', 'goodbye', 'ttyl'}
            if exit_commands.intersection(words):
                goodbye = "Closing ARYA interface. Goodbye."
                print(f"\nARYA: {goodbye}")
                voice.speak(goodbye)
                import os
                os._exit(0)
                
            # Process via Gemini Core
            response = brain.process_input(user_input)
            
            print(f"\nARYA: {response}")
            voice.speak(response)
            
        except KeyboardInterrupt:
            print("\n[SYSTEM]: Force quitting via KeyboardInterrupt...")
            break
        except Exception as e:
            print(f"\n[SYSTEM ERROR]: {e}")
