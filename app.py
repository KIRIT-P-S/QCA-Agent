from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import os
import json
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import re
from urllib.parse import urlparse, urljoin
import threading
import queue

app = Flask(__name__)
# app.config['SECRET_KEY'] = 'your-secret-key-here'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Global variables for storing validation results
validation_results = {}
current_validation_id = None

class PRDValidator:
    def __init__(self):
        self.results = {
            'overall_status': 'pending',
            'tests': [],
            'summary': {
                'total_tests': 0,
                'passed': 0,
                'failed': 0,
                'warnings': 0
            }
        }
    
    def validate_website(self, url, prd_content):
        """Main validation method"""
        try:
            # Initialize webdriver
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Navigate to website
            driver.get(url)
            time.sleep(3)  # Wait for page to load
            
            # Get page content
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Extract PRD requirements
            requirements = self.extract_requirements(prd_content)
            
            # Run validation tests
            self.run_validation_tests(driver, soup, requirements, url)
            
            driver.quit()
            
            # Calculate overall status
            self.calculate_overall_status()
            
            return self.results
            
        except Exception as e:
            self.results['overall_status'] = 'error'
            self.results['error_message'] = str(e)
            return self.results
    
    def extract_requirements(self, prd_content):
        """Extract requirements from PRD content"""
        requirements = []
        
        # Simple keyword-based extraction
        keywords = [
            'button', 'form', 'input', 'link', 'image', 'text', 'title',
            'header', 'footer', 'navigation', 'menu', 'search', 'login',
            'register', 'contact', 'about', 'home', 'product', 'service'
        ]
        
        lines = prd_content.split('\n')
        for line in lines:
            line = line.strip().lower()
            if any(keyword in line for keyword in keywords):
                requirements.append(line)
        
        return requirements
    
    def run_validation_tests(self, driver, soup, requirements, url):
        """Run various validation tests"""
        tests = []
        
        # Test 1: Website Accessibility
        tests.append(self.test_website_accessibility(driver, url))
        
        # Test 2: Page Title
        tests.append(self.test_page_title(soup))
        
        # Test 3: Meta Tags
        tests.append(self.test_meta_tags(soup))
        
        # Test 4: Links Validation
        tests.append(self.test_links(soup, url))
        
        # Test 5: Images
        tests.append(self.test_images(soup, url))
        
        # Test 6: Forms
        tests.append(self.test_forms(soup))
        
        # Test 7: Responsive Design
        tests.append(self.test_responsive_design(driver))
        
        # Test 8: Performance
        tests.append(self.test_performance(driver))
        
        # Test 9: SEO Elements
        tests.append(self.test_seo_elements(soup))
        
        # Test 10: Content Requirements
        tests.append(self.test_content_requirements(soup, requirements))
        
        self.results['tests'] = tests
        self.results['summary']['total_tests'] = len(tests)
    
    def test_website_accessibility(self, driver, url):
        """Test if website is accessible"""
        try:
            response = requests.get(url, timeout=10)
            status = 'passed' if response.status_code == 200 else 'failed'
            return {
                'name': 'Website Accessibility',
                'status': status,
                'details': f'Status code: {response.status_code}',
                'description': 'Check if the website is accessible and responding'
            }
        except Exception as e:
            return {
                'name': 'Website Accessibility',
                'status': 'failed',
                'details': f'Error: {str(e)}',
                'description': 'Check if the website is accessible and responding'
            }
    
    def test_page_title(self, soup):
        """Test page title"""
        title = soup.find('title')
        if title and title.text.strip():
            return {
                'name': 'Page Title',
                'status': 'passed',
                'details': f'Title: {title.text.strip()}',
                'description': 'Check if page has a title'
            }
        else:
            return {
                'name': 'Page Title',
                'status': 'failed',
                'details': 'No title found',
                'description': 'Check if page has a title'
            }
    
    def test_meta_tags(self, soup):
        """Test meta tags"""
        meta_tags = soup.find_all('meta')
        important_meta = ['description', 'keywords', 'viewport', 'robots']
        found_meta = []
        
        for meta in meta_tags:
            if meta.get('name') in important_meta or meta.get('property') in important_meta:
                found_meta.append(meta.get('name') or meta.get('property'))
        
        if len(found_meta) >= 2:
            return {
                'name': 'Meta Tags',
                'status': 'passed',
                'details': f'Found meta tags: {", ".join(found_meta)}',
                'description': 'Check for important meta tags'
            }
        else:
            return {
                'name': 'Meta Tags',
                'status': 'warning',
                'details': f'Found only {len(found_meta)} important meta tags',
                'description': 'Check for important meta tags'
            }
    
    def test_links(self, soup, base_url):
        """Test links on the page"""
        links = soup.find_all('a', href=True)
        valid_links = 0
        broken_links = 0
        
        for link in links[:10]:  # Test first 10 links
            href = link['href']
            if href.startswith('http'):
                try:
                    response = requests.head(href, timeout=5)
                    if response.status_code == 200:
                        valid_links += 1
                    else:
                        broken_links += 1
                except:
                    broken_links += 1
            elif href.startswith('/'):
                try:
                    full_url = urljoin(base_url, href)
                    response = requests.head(full_url, timeout=5)
                    if response.status_code == 200:
                        valid_links += 1
                    else:
                        broken_links += 1
                except:
                    broken_links += 1
        
        if broken_links == 0:
            status = 'passed'
        elif broken_links <= 2:
            status = 'warning'
        else:
            status = 'failed'
        
        return {
            'name': 'Links Validation',
            'status': status,
            'details': f'Valid: {valid_links}, Broken: {broken_links}',
            'description': 'Check for broken links'
        }
    
    def test_images(self, soup, base_url):
        """Test images on the page"""
        images = soup.find_all('img')
        images_with_alt = 0
        
        for img in images:
            if img.get('alt'):
                images_with_alt += 1
        
        if len(images) == 0:
            return {
                'name': 'Images',
                'status': 'warning',
                'details': 'No images found',
                'description': 'Check images have alt text'
            }
        
        alt_percentage = (images_with_alt / len(images)) * 100
        
        if alt_percentage >= 90:
            status = 'passed'
        elif alt_percentage >= 70:
            status = 'warning'
        else:
            status = 'failed'
        
        return {
            'name': 'Images',
            'status': status,
            'details': f'{images_with_alt}/{len(images)} images have alt text ({alt_percentage:.1f}%)',
            'description': 'Check images have alt text'
        }
    
    def test_forms(self, soup):
        """Test forms on the page"""
        forms = soup.find_all('form')
        
        if len(forms) == 0:
            return {
                'name': 'Forms',
                'status': 'warning',
                'details': 'No forms found',
                'description': 'Check forms have proper structure'
            }
        
        valid_forms = 0
        for form in forms:
            inputs = form.find_all('input')
            if len(inputs) > 0:
                valid_forms += 1
        
        if valid_forms == len(forms):
            status = 'passed'
        else:
            status = 'warning'
        
        return {
            'name': 'Forms',
            'status': status,
            'details': f'{valid_forms}/{len(forms)} forms have inputs',
            'description': 'Check forms have proper structure'
        }
    
    def test_responsive_design(self, driver):
        """Test responsive design"""
        try:
            # Test different screen sizes
            screen_sizes = [(1920, 1080), (1366, 768), (768, 1024), (375, 667)]
            responsive_score = 0
            
            for width, height in screen_sizes:
                driver.set_window_size(width, height)
                time.sleep(1)
                
                # Check if page loads without horizontal scroll
                body_width = driver.execute_script("return document.body.scrollWidth")
                viewport_width = driver.execute_script("return window.innerWidth")
                
                if body_width <= viewport_width:
                    responsive_score += 1
            
            percentage = (responsive_score / len(screen_sizes)) * 100
            
            if percentage >= 75:
                status = 'passed'
            elif percentage >= 50:
                status = 'warning'
            else:
                status = 'failed'
            
            return {
                'name': 'Responsive Design',
                'status': status,
                'details': f'Responsive score: {percentage:.1f}%',
                'description': 'Check responsive design across screen sizes'
            }
        except Exception as e:
            return {
                'name': 'Responsive Design',
                'status': 'failed',
                'details': f'Error: {str(e)}',
                'description': 'Check responsive design across screen sizes'
            }
    
    def test_performance(self, driver):
        """Test page performance"""
        try:
            # Get page load time
            start_time = time.time()
            driver.refresh()
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            load_time = time.time() - start_time
            
            if load_time < 3:
                status = 'passed'
            elif load_time < 5:
                status = 'warning'
            else:
                status = 'failed'
            
            return {
                'name': 'Performance',
                'status': status,
                'details': f'Load time: {load_time:.2f}s',
                'description': 'Check page load performance'
            }
        except Exception as e:
            return {
                'name': 'Performance',
                'status': 'failed',
                'details': f'Error: {str(e)}',
                'description': 'Check page load performance'
            }
    
    def test_seo_elements(self, soup):
        """Test SEO elements"""
        seo_score = 0
        total_checks = 4
        
        # Check for h1 tag
        if soup.find('h1'):
            seo_score += 1
        
        # Check for meta description
        if soup.find('meta', attrs={'name': 'description'}):
            seo_score += 1
        
        # Check for canonical link
        if soup.find('link', attrs={'rel': 'canonical'}):
            seo_score += 1
        
        # Check for structured data
        if soup.find_all(attrs={'itemtype': True}):
            seo_score += 1
        
        percentage = (seo_score / total_checks) * 100
        
        if percentage >= 75:
            status = 'passed'
        elif percentage >= 50:
            status = 'warning'
        else:
            status = 'failed'
        
        return {
            'name': 'SEO Elements',
            'status': status,
            'details': f'SEO score: {seo_score}/{total_checks} ({percentage:.1f}%)',
            'description': 'Check for important SEO elements'
        }
    
    def test_content_requirements(self, soup, requirements):
        """Test content against PRD requirements"""
        if not requirements:
            return {
                'name': 'Content Requirements',
                'status': 'warning',
                'details': 'No specific requirements found in PRD',
                'description': 'Check content against PRD requirements'
            }
        
        content_text = soup.get_text().lower()
        found_requirements = []
        
        for req in requirements:
            if any(word in content_text for word in req.split()):
                found_requirements.append(req)
        
        if len(found_requirements) >= len(requirements) * 0.7:
            status = 'passed'
        elif len(found_requirements) >= len(requirements) * 0.4:
            status = 'warning'
        else:
            status = 'failed'
        
        return {
            'name': 'Content Requirements',
            'status': status,
            'details': f'Found {len(found_requirements)}/{len(requirements)} requirements',
            'description': 'Check content against PRD requirements'
        }
    
    def calculate_overall_status(self):
        """Calculate overall validation status"""
        passed = sum(1 for test in self.results['tests'] if test['status'] == 'passed')
        failed = sum(1 for test in self.results['tests'] if test['status'] == 'failed')
        warnings = sum(1 for test in self.results['tests'] if test['status'] == 'warning')
        
        self.results['summary']['passed'] = passed
        self.results['summary']['failed'] = failed
        self.results['summary']['warnings'] = warnings
        
        if failed == 0 and warnings == 0:
            self.results['overall_status'] = 'passed'
        elif failed == 0:
            self.results['overall_status'] = 'warning'
        else:
            self.results['overall_status'] = 'failed'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/validate', methods=['POST'])
def validate_website():
    try:
        data = request.get_json()
        website_url = data.get('website_url')
        prd_content = data.get('prd_content')
        
        if not website_url or not prd_content:
            return jsonify({'error': 'Both website URL and PRD content are required'}), 400
        
        # Create validator instance
        validator = PRDValidator()
        
        # Run validation
        results = validator.validate_website(website_url, prd_content)
        
        return jsonify(results)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/upload-prd', methods=['POST'])
def upload_prd():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Read file content
        content = file.read().decode('utf-8')
        
        return jsonify({'content': content})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000) 