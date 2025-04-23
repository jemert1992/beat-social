import os
import time
import logging
import schedule
from src.system import SocialMediaAutomationSystem

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("worker.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("worker")

def run_scheduler():
    """Run the scheduler to process pending posts"""
    logger.info("Running scheduler")
    
    try:
        # Initialize the social media automation system
        base_dir = os.path.dirname(os.path.abspath(__file__))
        system = SocialMediaAutomationSystem(base_dir)
        
        # Start the scheduler
        system.scheduler.start_scheduler()
        
        logger.info("Scheduler started successfully")
        return True
    except Exception as e:
        logger.error(f"Error starting scheduler: {str(e)}")
        return False

def run_weekly_report():
    """Generate weekly performance reports"""
    logger.info("Generating weekly reports")
    
    try:
        # Initialize the social media automation system
        base_dir = os.path.dirname(os.path.abspath(__file__))
        system = SocialMediaAutomationSystem(base_dir)
        
        # Generate report
        report_path = system.generate_weekly_report()
        
        logger.info(f"Weekly report generated: {report_path}")
        return True
    except Exception as e:
        logger.error(f"Error generating weekly report: {str(e)}")
        return False

def run_trend_analysis():
    """Run trend analysis to update content recommendations"""
    logger.info("Running trend analysis")
    
    try:
        # Initialize the social media automation system
        base_dir = os.path.dirname(os.path.abspath(__file__))
        system = SocialMediaAutomationSystem(base_dir)
        
        # Analyze trends
        trend_analysis = system.content_analyzer.analyze_all_platforms()
        
        logger.info("Trend analysis completed successfully")
        return True
    except Exception as e:
        logger.error(f"Error running trend analysis: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("Starting worker process")
    
    # Run scheduler immediately
    run_scheduler()
    
    # Schedule tasks
    schedule.every(1).hours.do(run_scheduler)
    schedule.every().sunday.at("00:00").do(run_weekly_report)
    schedule.every().day.at("01:00").do(run_trend_analysis)
    
    logger.info("Worker tasks scheduled")
    
    # Keep the worker running
    while True:
        schedule.run_pending()
        time.sleep(60)
