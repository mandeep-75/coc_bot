from starting_sequence.starting_sequence import StartingSequence
from search_sequence.search_sequence import SearchSequence
from attack_sequence.attack_sequence import AttackSequence
import logging
import time

# Basic logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)

def main():
    logging.info("STARTING CLASH OF CLANS ASSISTANT")
    # Setup game parameters
    start_sequence = StartingSequence()
    attack_sequence = AttackSequence(target_percentage=50) 

    try:
        while True:
            # First make sure we're at home base
            start_sequence.navigate_to_home()
            
            # Collect available resources
            logging.info("Collecting resources...")
            start_sequence.collect_resources()
            
            # Return home before starting attacks
            start_sequence.navigate_to_home()
            
            # Run an attack cycle
            logging.info("Starting attack...")
            attack_sequence.execute_attack_cycle()
            

    except KeyboardInterrupt:
        logging.info("USER INTERRUPTED EXECUTION")
    except Exception as e:
        logging.error(f"Error: {e}")
    finally:
        # Note: Need to create this function or remove this line
        # train_sequence.cleanup()  
        logging.info("ASSISTANT STOPPED")

if __name__ == "__main__":
    main()
