import logging
import time
import sys
from typing import Optional, Dict, Any
from dataclasses import dataclass
from starting_sequence.starting_sequence import StartingSequence
from search_sequence.search_sequence import SearchSequence
from attack_sequence.attack_sequence import AttackSequence
from donation_sequence.donation_sequence import DonationSequence

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
    # General settings
    debug_mode: bool = False
    max_cycles: Optional[int] = None
    cycle_delay: float = 2.0
    
    # Sequence toggles
    enable_starting: bool = True
    enable_searching: bool = True
    enable_attacking: bool = True
    enable_donations: bool = False
    
    # Attack settings
    target_percentage: int = 50
    max_searches: int = 30000
    
    # Resource thresholds
    gold_threshold: int = 100000
    elixir_threshold: int = 100000
    dark_threshold: int = 5000
    
    # Donation settings
    donation_interval: int = 3

class ClashBot:
    def __init__(self, config: BotConfig):
        """
        Initialize the Clash of Clans bot with configuration options.
        
        Args:
            config: BotConfig object containing all bot settings
        """
        self.config = config
        self.running = False
        self.attack_count = 0
        
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
        self.donation_sequence = DonationSequence(debug_mode=config.debug_mode)
        
        logging.info("=" * 50)
        logging.info("CLASH OF CLANS BOT INITIALIZED")
        logging.info(f"Debug Mode: {'Enabled' if config.debug_mode else 'Disabled'}")
        logging.info("\nSequence Status:")
        logging.info(f"  Starting Sequence: {'Enabled' if config.enable_starting else 'Disabled'}")
        logging.info(f"  Search Sequence: {'Enabled' if config.enable_searching else 'Disabled'}")
        logging.info(f"  Attack Sequence: {'Enabled' if config.enable_attacking else 'Disabled'}")
        logging.info(f"  Donation Sequence: {'Enabled' if config.enable_donations else 'Disabled'}")
        
        if config.enable_searching or config.enable_attacking:
            logging.info("\nResource Thresholds:")
            logging.info(f"  Gold: {config.gold_threshold:,}")
            logging.info(f"  Elixir: {config.elixir_threshold:,}")
            logging.info(f"  Dark: {config.dark_threshold:,}")
            logging.info(f"Target Destruction: {config.target_percentage}%")
        
        if config.enable_donations:
            logging.info(f"\nDonation Settings:")
            logging.info(f"  Donation Interval: Every {config.donation_interval} attacks")
        
        logging.info("=" * 50)

    def setup(self) -> bool:
        """Perform initial setup and verification."""
        try:
            logging.info("Performing initial setup...")
            
            # Only navigate to home if starting sequence is enabled
            if self.config.enable_starting:
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
        """Collect available resources from the home base."""
        if not self.config.enable_starting:
            return True
            
        try:
            logging.info("Collecting resources...")
            return self.start_sequence.collect_resources()
        except Exception as e:
            logging.error(f"Resource collection failed: {str(e)}")
            return False

    def execute_attack_cycle(self) -> bool:
        """Execute a complete attack cycle: search, attack, and return."""
        try:
            logging.info("Starting attack cycle...")
            
            # Ensure we're at home base if starting sequence is enabled
            if self.config.enable_starting:
                if not self.start_sequence.navigate_to_home():
                    logging.error("Failed to navigate to home before attack")
                    return False
            
            # Execute attack if enabled
            if self.config.enable_attacking:
                attack_success = self.attack_sequence.execute_attack_cycle(
                    max_searches=self.config.max_searches
                )
                
                if attack_success:
                    self.attack_count += 1
                    
                    # Check if it's time to donate
                    if (self.config.enable_donations and 
                        self.attack_count >= self.config.donation_interval):
                        logging.info(f"Attack count reached {self.attack_count}, executing donation cycle")
                        self.donation_sequence.execute_donation_cycle()
                        self.attack_count = 0  # Reset attack count
                else:
                    logging.warning("Attack cycle completed with issues")
                    return False
            else:
                logging.info("Attack sequence is disabled")
                return True
                
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
                try:
                    # Check if we've reached max cycles
                    if self.config.max_cycles and cycle_count >= self.config.max_cycles:
                        logging.info(f"Reached maximum cycles ({self.config.max_cycles})")
                        break
                        
                    # Execute one complete cycle
                    logging.info(f"\nStarting cycle {cycle_count + 1}")
                    
                    # Validate game state before operations if starting sequence is enabled
                    if self.config.enable_starting:
                        if not self.start_sequence.check_game_state():
                            logging.error("Game state validation failed - attempting recovery")
                            if not self.start_sequence.navigate_to_home():
                                raise RuntimeError("Failed to recover game state")
                    
                    # Collect resources if starting sequence is enabled
                    if self.config.enable_starting:
                        retry_count = 0
                        while retry_count < 3:
                            if self.collect_resources():
                                break
                            retry_count += 1
                            time.sleep(1)
                        if retry_count == 3:
                            logging.error("Failed to collect resources after 3 attempts")
                    
                    # Execute attack cycle if enabled
                    if self.config.enable_attacking or self.config.enable_searching:
                        if not self.execute_attack_cycle():
                            logging.error("Attack cycle failed - attempting recovery")
                            if self.config.enable_starting and not self.start_sequence.navigate_to_home():
                                raise RuntimeError("Failed to recover after attack cycle")
                    
                    # Handle donations independently if only donations are enabled
                    if self.config.enable_donations and not (self.config.enable_attacking or self.config.enable_searching):
                        logging.info("Executing donation cycle...")
                        if not self.donation_sequence.execute_donation_cycle():
                            logging.error("Donation cycle failed")
                            if self.config.enable_starting and not self.start_sequence.navigate_to_home():
                                raise RuntimeError("Failed to recover after donation cycle")
                    
                    cycle_count += 1
                    
                    # Delay between cycles
                    time.sleep(self.config.cycle_delay)
                    
                except Exception as cycle_error:
                    logging.error(f"Error during cycle {cycle_count + 1}: {str(cycle_error)}")
                    # Attempt recovery if starting sequence is enabled
                    if self.config.enable_starting:
                        if not self.start_sequence.navigate_to_home():
                            raise RuntimeError("Failed to recover after cycle error")
                    time.sleep(2)  # Additional delay after recovery
                    
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
        cycle_delay=2.0,
        
        # Sequence toggles
        enable_starting=True,
        enable_searching=True,
        enable_attacking=True,
        enable_donations=False,
        
        # Attack settings
        target_percentage=50,
        max_searches=30000,
        
        # Resource thresholds
        gold_threshold=100000,
        elixir_threshold=100000,
        dark_threshold=5000,
        
        # Donation settings
        donation_interval=3
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