from flask import Flask, request, jsonify, render_template
import os
import logging
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
    return jsonify({
        "status": "online",
        "version": "1.0.0",
        "config": system.config
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
