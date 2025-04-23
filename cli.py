import os
import sys
import argparse
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
        logging.FileHandler("social_media_cli.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("social_media_cli")

def main():
    """
    Command-line interface for the Social Media Content Automation System.
    """
    parser = argparse.ArgumentParser(description='Social Media Content Automation System')
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Configure command
    configure_parser = subparsers.add_parser('configure', help='Configure the system')
    configure_parser.add_argument('--niche', required=True, help='Content niche (e.g., weddings, fitness, travel)')
    configure_parser.add_argument('--tiktok-frequency', type=int, default=1, help='Number of TikTok posts per day')
    configure_parser.add_argument('--instagram-frequency', type=int, default=1, help='Number of Instagram posts per day')
    
    # Plan command
    plan_parser = subparsers.add_parser('plan', help='Generate a content plan')
    plan_parser.add_argument('--days', type=int, default=7, help='Number of days to plan for')
    
    # Execute command
    execute_parser = subparsers.add_parser('execute', help='Execute the content plan')
    execute_parser.add_argument('--plan-file', help='Path to content plan file (optional)')
    
    # Report command
    report_parser = subparsers.add_parser('report', help='Generate a weekly report')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Initialize system
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    system = SocialMediaAutomationSystem(base_dir)
    
    # Execute command
    if args.command == 'configure':
        # Configure the system
        system.configure(
            niche=args.niche,
            tiktok_frequency=args.tiktok_frequency,
            instagram_frequency=args.instagram_frequency
        )
        print(f"System configured for niche: {args.niche}")
        print(f"TikTok posts per day: {args.tiktok_frequency}")
        print(f"Instagram posts per day: {args.instagram_frequency}")
        
    elif args.command == 'plan':
        # Generate a content plan
        content_plan = system.generate_content_plan(days=args.days)
        print(f"Content plan generated for {args.days} days")
        print(f"TikTok posts: {content_plan['tiktok']['total_posts']}")
        print(f"Instagram posts: {content_plan['instagram']['total_posts']}")
        print(f"Plan saved to: {os.path.join(system.data_dir, f'content_plan_{datetime.now().strftime('%Y%m%d')}.json')}")
        
    elif args.command == 'execute':
        # Execute the content plan
        if args.plan_file:
            # Load plan from file
            import json
            with open(args.plan_file, 'r') as f:
                content_plan = json.load(f)
            print(f"Executing content plan from file: {args.plan_file}")
        else:
            # Generate a new plan
            content_plan = system.generate_content_plan()
            print("Executing newly generated content plan")
        
        # Execute the plan
        execution_results = system.execute_content_plan(content_plan)
        print("Content plan execution completed")
        print(f"TikTok posts generated: {len(execution_results['tiktok']['generated'])}")
        print(f"TikTok posts scheduled: {len(execution_results['tiktok']['scheduled'])}")
        print(f"Instagram posts generated: {len(execution_results['instagram']['generated'])}")
        print(f"Instagram posts scheduled: {len(execution_results['instagram']['scheduled'])}")
        
    elif args.command == 'report':
        # Generate a weekly report
        report_path = system.generate_weekly_report()
        print(f"Weekly report generated: {report_path}")
        
    else:
        # Show help if no command specified
        parser.print_help()

if __name__ == "__main__":
    main()
