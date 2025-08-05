# PRD Validation Agent

A comprehensive web application that validates websites against Product Requirements Documents (PRD) using Python Flask backend and a modern, responsive frontend.

## Features

- **Website Validation**: Tests websites against PRD requirements
- **Comprehensive Testing**: 10 different validation tests including accessibility, SEO, performance, and more
- **Real-time Results**: Beautiful, interactive results display
- **File Upload Support**: Upload PRD documents in various formats
- **Responsive Design**: Works on desktop and mobile devices
- **Modern UI**: Clean, professional interface with smooth animations

## Validation Tests

The agent performs the following tests:

1. **Website Accessibility** - Checks if the website is accessible and responding
2. **Page Title** - Validates presence and content of page title
3. **Meta Tags** - Checks for important meta tags (description, keywords, viewport, robots)
4. **Links Validation** - Tests for broken links on the page
5. **Images** - Validates image alt text for accessibility
6. **Forms** - Checks form structure and input elements
7. **Responsive Design** - Tests responsive behavior across different screen sizes
8. **Performance** - Measures page load time
9. **SEO Elements** - Validates SEO best practices (H1 tags, meta descriptions, etc.)
10. **Content Requirements** - Matches website content against PRD requirements

## Installation

### Prerequisites

- Python 3.8 or higher
- Chrome browser (for Selenium WebDriver)
- pip (Python package installer)

### Setup

1. **Clone or download the project**
   ```bash
   git clone https://github.com/KIRIT-P-S/QCA-Agent.git
   cd prd-validation-agent
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:5000`

## Usage

### Basic Usage

1. **Enter Website URL**: Provide the URL of the website you want to validate
2. **Add PRD Content**: Either paste your PRD content directly or upload a file
3. **Start Validation**: Click the "Start Validation" button
4. **View Results**: See real-time validation results with pass/fail status

### PRD Content Format

The agent can process PRD content in various formats:
- Plain text
- Word documents (.doc, .docx)
- PDF files
- Rich text format

### Understanding Results

- **Passed (Green)**: Test completed successfully
- **Failed (Red)**: Test failed and needs attention
- **Warning (Yellow)**: Test completed but with minor issues
- **Overall Status**: Summary of all test results

## API Endpoints

### POST /validate
Validates a website against PRD content.

**Request Body:**
```json
{
  "website_url": "https://example.com",
  "prd_content": "Your PRD content here..."
}
```

**Response:**
```json
{
  "overall_status": "passed|failed|warning",
  "summary": {
    "total_tests": 10,
    "passed": 8,
    "failed": 1,
    "warnings": 1
  },
  "tests": [
    {
      "name": "Website Accessibility",
      "status": "passed",
      "details": "Status code: 200",
      "description": "Check if the website is accessible and responding"
    }
  ]
}
```

### POST /upload-prd
Uploads and processes a PRD file.

**Request:** Multipart form data with file

**Response:**
```json
{
  "content": "Extracted text content from the file"
}
```

## Configuration

### Environment Variables

You can configure the application using environment variables:

- `FLASK_ENV`: Set to `development` for debug mode
- `FLASK_DEBUG`: Enable/disable debug mode
- `SECRET_KEY`: Flask secret key for sessions

### Customization

You can customize the validation tests by modifying the `PRDValidator` class in `app.py`:

- Add new test methods
- Modify existing test criteria
- Adjust scoring thresholds
- Add custom requirements extraction

## Troubleshooting

### Common Issues

1. **ChromeDriver not found**
   - The application automatically downloads ChromeDriver
   - Ensure Chrome browser is installed
   - Check internet connection for automatic download

2. **Port already in use**
   - Change the port in `app.py` line: `socketio.run(app, debug=True, host='0.0.0.0', port=5000)`

3. **Permission errors**
   - Run with appropriate permissions
   - Check firewall settings

4. **Slow validation**
   - Some tests require loading the website multiple times
   - Network speed affects validation time
   - Consider running on faster internet connection

### Performance Tips

- Use headless Chrome for faster execution
- Limit the number of links tested (currently set to 10)
- Adjust timeouts for different network conditions
- Consider running validation during off-peak hours

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Check the troubleshooting section
- Review the code comments
- Create an issue in the repository

## Future Enhancements

- Support for more file formats
- Custom test configuration
- Batch validation for multiple websites
- Export results to PDF/Excel
- Integration with CI/CD pipelines
- Advanced SEO analysis
- Accessibility compliance checking

- Performance benchmarking 
