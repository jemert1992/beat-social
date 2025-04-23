import os
import threading
import time
import logging
import schedule
from flask import Flask, request, jsonify, render_template
from src.system import SocialMediaAutomationSystem

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("app")

# Initialize Flask app
app = Flask(__name__)

# Initialize the social media automation system
base_dir = os.path.dirname(os.path.abspath(__file__))
system = SocialMediaAutomationSystem(base_dir)

# Worker functions
def run_scheduler():
    """Run the scheduler to process pending posts"""
    logger.info("Running scheduler")
    
    try:
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
        # Analyze trends
        trend_analysis = system.content_analyzer.analyze_all_platforms()
        
        logger.info("Trend analysis completed successfully")
        return True
    except Exception as e:
        logger.error(f"Error running trend analysis: {str(e)}")
        return False

def worker_thread():
    """Background worker thread function"""
    logger.info("Starting worker thread")
    
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

# Start worker thread if enabled
if os.environ.get('ENABLE_WORKER', 'false').lower() == 'true':
    worker = threading.Thread(target=worker_thread, daemon=True)
    worker.start()
    logger.info("Background worker thread started")

# Web routes
@app.route('/')
def home():
    """Home page route"""
    return render_template('index.html')

@app.route('/api/configure', methods=['POST'])
def configure():
    """Configure the system"""
    data = request.json
    
    try:
        system.configure(
            niche=data.get('niche', 'general'),
            tiktok_frequency=int(data.get('tiktok_frequency', 1)),
            instagram_frequency=int(data.get('instagram_frequency', 1)),
            content_preferences=data.get('content_preferences', {})
        )
        return jsonify({"status": "success", "message": "System configured successfully"})
    except Exception as e:
        logger.error(f"Configuration error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/plan', methods=['POST'])
def generate_plan():
    """Generate a content plan"""
    data = request.json
    
    try:
        days = int(data.get('days', 7))
        content_plan = system.generate_content_plan(days=days)
        return jsonify({"status": "success", "plan": content_plan})
    except Exception as e:
        logger.error(f"Plan generation error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/execute', methods=['POST'])
def execute_plan():
    """Execute a content plan"""
    data = request.json
    
    try:
        content_plan = data.get('plan')
        if content_plan:
            execution_results = system.execute_content_plan(content_plan)
        else:
            execution_results = system.execute_content_plan()
            
        return jsonify({"status": "success", "results": execution_results})
    except Exception as e:
        logger.error(f"Plan execution error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/report', methods=['GET'])
def generate_report():
    """Generate a weekly report"""
    try:
        report_path = system.generate_weekly_report()
        return jsonify({"status": "success", "report_path": report_path})
    except Exception as e:
        logger.error(f"Report generation error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/status', methods=['GET'])
def status():
    """Check system status"""
    worker_status = "running" if os.environ.get('ENABLE_WORKER', 'false').lower() == 'true' else "disabled"
    
    return jsonify({
        "status": "online",
        "version": "1.0.0",
        "worker": worker_status,
        "config": system.config
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
