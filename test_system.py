import os
import sys
import logging
from datetime import datetime

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.system import SocialMediaAutomationSystem

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("test_system.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("test_system")

def test_system():
    """
    Test the functionality of the social media automation system.
    """
    logger.info("Starting system test")
    
    # Initialize system
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    system = SocialMediaAutomationSystem(base_dir)
    
    # Test configuration
    logger.info("Testing system configuration")
    system.configure(
        niche="travel",
        tiktok_frequency=2,
        instagram_frequency=1,
        content_preferences={
            "preferred_content_types": ["tutorial", "showcase"],
            "preferred_themes": ["adventure", "budget"]
        }
    )
    
    # Test content plan generation
    logger.info("Testing content plan generation")
    content_plan = system.generate_content_plan(days=3)
    
    # Verify content plan
    assert content_plan["niche"] == "travel"
    assert content_plan["tiktok"]["posts_per_day"] == 2
    assert content_plan["instagram"]["posts_per_day"] == 1
    assert len(content_plan["tiktok"]["posts"]) == 6  # 2 posts/day * 3 days
    assert len(content_plan["instagram"]["posts"]) == 3  # 1 post/day * 3 days
    
    logger.info("Content plan generation test passed")
    
    # Test content plan execution (limited to 1 post per platform for testing)
    logger.info("Testing content plan execution (limited sample)")
    
    # Create a small test plan
    test_plan = {
        "niche": "travel",
        "period": f"{datetime.now().strftime('%Y-%m-%d')} to {(datetime.now()).strftime('%Y-%m-%d')}",
        "tiktok": {
            "posts_per_day": 1,
            "total_posts": 1,
            "content_types": ["tutorial", "showcase"],
            "themes": ["adventure", "budget"],
            "hashtags": ["#travel", "#adventure", "#budget"],
            "posts": [
                {
                    "id": "tiktok_test_1",
                    "content_type": "tutorial",
                    "theme": "adventure",
                    "day": 1,
                    "status": "planned"
                }
            ]
        },
        "instagram": {
            "posts_per_day": 1,
            "total_posts": 1,
            "content_types": ["carousel", "single_image"],
            "themes": ["adventure", "photography"],
            "hashtags": ["#travel", "#adventure", "#photography"],
            "posts": [
                {
                    "id": "instagram_test_1",
                    "content_type": "carousel",
                    "theme": "adventure",
                    "day": 1,
                    "status": "planned"
                }
            ]
        }
    }
    
    # Execute the test plan
    execution_results = system.execute_content_plan(test_plan)
    
    # Verify execution results
    assert len(execution_results["tiktok"]["generated"]) == 1
    assert len(execution_results["tiktok"]["scheduled"]) == 1
    assert len(execution_results["instagram"]["generated"]) == 1
    assert len(execution_results["instagram"]["scheduled"]) == 1
    
    logger.info("Content plan execution test passed")
    
    # Test weekly report generation
    logger.info("Testing weekly report generation")
    report_path = system.generate_weekly_report()
    
    # Verify report was generated
    assert report_path is not None
    
    logger.info(f"Weekly report generation test passed: {report_path}")
    
    logger.info("All system tests passed successfully")
    return True

if __name__ == "__main__":
    test_system()
