import logging
import time
import sys
from typing import Optional, Dict, Any
from dataclasses import dataclass
from starting_sequence.starting_sequence import StartingSequence
from search_sequence.search_sequence import SearchSequence
from attack_sequence.attack_sequence import AttackSequence

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot.log')
    ]
)

@dataclass
class BotConfig:
    """Configuration settings for the Clash of Clans bot."""
    debug_mode: bool = False
    max_cycles: Optional[int] = None
    target_percentage: int = 50
    gold_threshold: int = 100000
    elixir_threshold: int = 100000
    dark_threshold: int = 5000
    max_searches: int = 30000
    cycle_delay: float = 2.0

class ClashBot:
    def __init__(self, config: BotConfig):
        """
        Initialize the Clash of Clans bot with configuration options.
        
        Args:
            config: BotConfig object containing all bot settings
        """
        self.config = config
        self.running = False
        
        # Initialize sequences with proper configuration
        self.start_sequence = StartingSequence(debug_mode=config.debug_mode)
        self.search_sequence = SearchSequence(
            gold_threshold=config.gold_threshold,
            elixir_threshold=config.elixir_threshold,
            dark_threshold=config.dark_threshold,
            debug_mode=config.debug_mode
        )
        self.attack_sequence = AttackSequence(
            target_percentage=config.target_percentage,
            debug_mode=config.debug_mode
        )
        
        logging.info("=" * 50)
        logging.info("CLASH OF CLANS BOT INITIALIZED")
        logging.info(f"Debug Mode: {'Enabled' if config.debug_mode else 'Disabled'}")
        logging.info(f"Resource Thresholds:")
        logging.info(f"  Gold: {config.gold_threshold:,}")
        logging.info(f"  Elixir: {config.elixir_threshold:,}")
        logging.info(f"  Dark: {config.dark_threshold:,}")
        logging.info(f"Target Destruction: {config.target_percentage}%")
        logging.info("=" * 50)

    def setup(self) -> bool:
        """
        Perform initial setup and verification.
        
        Returns:
            bool: True if setup was successful
        """
        try:
            logging.info("Performing initial setup...")
            
            # Navigate to home screen
            if not self.start_sequence.navigate_to_home():
                logging.error("Failed to navigate to home screen during setup")
                return False
                
            # Verify game state
            if not self.start_sequence.check_game_state():
                logging.error("Game state verification failed")
                return False
                
            logging.info("Setup completed successfully")
            return True
            
        except Exception as e:
            logging.error(f"Setup failed: {str(e)}")
            return False

    def collect_resources(self) -> bool:
        """
        Collect available resources from the home base.
        
        Returns:
            bool: True if resource collection was successful
        """
        try:
            logging.info("Collecting resources...")
            return self.start_sequence.collect_resources()
        except Exception as e:
            logging.error(f"Resource collection failed: {str(e)}")
            return False

    def execute_attack_cycle(self) -> bool:
        """
        Execute a complete attack cycle: search, attack, and return.
        
        Returns:
            bool: True if the attack cycle was successful
        """
        try:
            logging.info("Starting attack cycle...")
            
            # Ensure we're at home base
            if not self.start_sequence.navigate_to_home():
                logging.error("Failed to navigate to home before attack")
                return False
                
            # Execute attack
            attack_success = self.attack_sequence.execute_attack_cycle(
                max_searches=self.config.max_searches
            )
            
            if not attack_success:
                logging.warning("Attack cycle completed with issues")
                return False
                
            logging.info("Attack cycle completed successfully")
            return True
            
        except Exception as e:
            logging.error(f"Attack cycle failed: {str(e)}")
            return False

    def run(self):
        """Run the bot with the configured settings."""
        self.running = True
        cycle_count = 0
        
        try:
            # Initial setup
            if not self.setup():
                logging.error("Initial setup failed - stopping bot")
                return
                
            while self.running:
                # Check if we've reached max cycles
                if self.config.max_cycles and cycle_count >= self.config.max_cycles:
                    logging.info(f"Reached maximum cycles ({self.config.max_cycles})")
                    break
                    
                # Execute one complete cycle
                logging.info(f"\nStarting cycle {cycle_count + 1}")
                
                # Collect resources
                self.collect_resources()
                
                # Execute attack cycle
                self.execute_attack_cycle()
                
                cycle_count += 1
                
                # Delay between cycles
                time.sleep(self.config.cycle_delay)
                
        except KeyboardInterrupt:
            logging.info("\nBot stopped by user")
        except Exception as e:
            logging.error(f"Bot stopped due to error: {str(e)}")
        finally:
            self.running = False
            logging.info("Bot shutdown complete")

def main():
    """Main entry point for the Clash of Clans bot."""
    # Default configuration
    config = BotConfig(
        debug_mode=False,
        max_cycles=None,  # Run indefinitely
        target_percentage=50,
        gold_threshold=100000,
        elixir_threshold=100000,
        dark_threshold=5000,
        max_searches=30000,
        cycle_delay=2.0
    )
    
    try:
        # Initialize and run bot
        bot = ClashBot(config)
        bot.run()
        
    except Exception as e:
        logging.error(f"Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 