# app.py - Flask Backend with Gemini API Integration

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime
import google.generativeai as genai
from PyPDF2 import PdfReader
from docx import Document
import io
import base64

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///procurement.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create upload directories
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'documents'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'logos'), exist_ok=True)

db = SQLAlchemy(app)

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'your-api-key-here')
genai.configure(api_key=GEMINI_API_KEY)

# Database Models
class ProcurementRecord(db.Model):
    __tablename__ = 'procurement_records'
    
    id = db.Column(db.Integer, primary_key=True)
    record_id = db.Column(db.String(100), unique=True, nullable=False)
    title = db.Column(db.String(500))
    file_no = db.Column(db.String(100))
    ad_dates = db.Column(db.String(200))
    ship_to_address = db.Column(db.Text)
    vendor_name = db.Column(db.String(300))
    remit_to_address = db.Column(db.Text)
    telephone_no = db.Column(db.String(50))
    federal_tax_id = db.Column(db.String(50))
    authorized_signature = db.Column(db.String(200))
    printed_name = db.Column(db.String(200))
    purchasing_address = db.Column(db.Text)
    purchasing_contact_name = db.Column(db.String(200))
    purchasing_phone = db.Column(db.String(50))
    purchasing_email = db.Column(db.String(200))
    bid_deadline = db.Column(db.String(200))
    status = db.Column(db.String(20), default='draft')
    document_path = db.Column(db.String(500))
    logo_path = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    approved_at = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.record_id,
            'title': self.title,
            'fileNo': self.file_no,
            'adDates': self.ad_dates,
            'shipToAddress': self.ship_to_address,
            'vendorName': self.vendor_name,
            'remitToAddress': self.remit_to_address,
            'telephoneNo': self.telephone_no,
            'federalTaxId': self.federal_tax_id,
            'authorizedSignature': self.authorized_signature,
            'printedName': self.printed_name,
            'purchasingAddress': self.purchasing_address,
            'purchasingContactName': self.purchasing_contact_name,
            'purchasingPhone': self.purchasing_phone,
            'purchasingEmail': self.purchasing_email,
            'bidDeadline': self.bid_deadline,
            'status': self.status,
            'documentPath': self.document_path,
            'logoPath': self.logo_path,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None,
            'approvedAt': self.approved_at.isoformat() if self.approved_at else None
        }

# Helper Functions
def extract_text_from_pdf(file_path):
    """Extract text from PDF file"""
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"Error extracting PDF: {str(e)}")
        return None

def extract_text_from_docx(file_path):
    """Extract text from DOCX file"""
    try:
        doc = Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    except Exception as e:
        print(f"Error extracting DOCX: {str(e)}")
        return None

def extract_with_gemini(text):
    """Extract structured data using Gemini API"""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        You are an AI assistant specialized in extracting procurement and contract information.
        Extract the following fields from the document text below. If a field is not found, return an empty string.
        
        Fields to extract:
        1. Title (full title of the procurement/contract)
        2. File Number (file no, reference number, or similar)
        3. Ad Dates (advertisement dates)
        4. Ship to Address
        5. Vendor Name
        6. Remit to Address
        7. Telephone Number
        8. Federal Tax ID
        9. Authorized Signature
        10. Printed Name
        11. Purchasing Address
        12. Purchasing Contact Name
        13. Purchasing Phone
        14. Purchasing Email
        15. Bid Deadline (date and time)
        
        Return the extracted information in JSON format with these exact keys:
        {{
            "title": "",
            "fileNo": "",
            "adDates": "",
            "shipToAddress": "",
            "vendorName": "",
            "remitToAddress": "",
            "telephoneNo": "",
            "federalTaxId": "",
            "authorizedSignature": "",
            "printedName": "",
            "purchasingAddress": "",
            "purchasingContactName": "",
            "purchasingPhone": "",
            "purchasingEmail": "",
            "bidDeadline": ""
        }}
        
        Document Text:
        {text[:5000]}  # Limit text to avoid token limits
        """
        
        response = model.generate_content(prompt)
        
        # Extract JSON from response
        response_text = response.text
        # Remove markdown code blocks if present
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]
        
        extracted_data = json.loads(response_text.strip())
        return extracted_data
        
    except Exception as e:
        print(f"Error with Gemini extraction: {str(e)}")
        return None

def allowed_file(filename, file_type):
    """Check if file extension is allowed"""
    if file_type == 'document':
        allowed_extensions = {'pdf', 'doc', 'docx'}
    elif file_type == 'logo':
        allowed_extensions = {'png', 'jpg', 'jpeg', 'svg', 'gif'}
    else:
        return False
    
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

# API Routes

@app.route('/api/upload-and-extract', methods=['POST'])
def upload_and_extract():
    """Upload document and extract data using Gemini API"""
    try:
        if 'document' not in request.files:
            return jsonify({'error': 'No document file provided'}), 400
        
        document = request.files['document']
        logo = request.files.get('logo')
        
        if document.filename == '':
            return jsonify({'error': 'No document selected'}), 400
        
        if not allowed_file(document.filename, 'document'):
            return jsonify({'error': 'Invalid document file type. Only PDF, DOC, DOCX allowed'}), 400
        
        # Save document
        doc_filename = secure_filename(document.filename)
        doc_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        doc_filename = f"{doc_timestamp}_{doc_filename}"
        doc_path = os.path.join(app.config['UPLOAD_FOLDER'], 'documents', doc_filename)
        document.save(doc_path)
        
        # Save logo if provided
        logo_path = None
        if logo and logo.filename != '' and allowed_file(logo.filename, 'logo'):
            logo_filename = secure_filename(logo.filename)
            logo_filename = f"{doc_timestamp}_{logo_filename}"
            logo_path = os.path.join(app.config['UPLOAD_FOLDER'], 'logos', logo_filename)
            logo.save(logo_path)
        
        # Extract text from document
        file_extension = doc_filename.rsplit('.', 1)[1].lower()
        
        if file_extension == 'pdf':
            text = extract_text_from_pdf(doc_path)
        elif file_extension in ['doc', 'docx']:
            text = extract_text_from_docx(doc_path)
        else:
            return jsonify({'error': 'Unsupported file format'}), 400
        
        if not text:
            return jsonify({'error': 'Could not extract text from document'}), 500
        
        # Extract structured data using Gemini
        extracted_data = extract_with_gemini(text)
        
        if not extracted_data:
            return jsonify({'error': 'Could not extract data from document'}), 500
        
        # Generate unique record ID
        record_id = f"PROC_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Create database record
        record = ProcurementRecord(
            record_id=record_id,
            title=extracted_data.get('title', ''),
            file_no=extracted_data.get('fileNo', ''),
            ad_dates=extracted_data.get('adDates', ''),
            ship_to_address=extracted_data.get('shipToAddress', ''),
            vendor_name=extracted_data.get('vendorName', ''),
            remit_to_address=extracted_data.get('remitToAddress', ''),
            telephone_no=extracted_data.get('telephoneNo', ''),
            federal_tax_id=extracted_data.get('federalTaxId', ''),
            authorized_signature=extracted_data.get('authorizedSignature', ''),
            printed_name=extracted_data.get('printedName', ''),
            purchasing_address=extracted_data.get('purchasingAddress', ''),
            purchasing_contact_name=extracted_data.get('purchasingContactName', ''),
            purchasing_phone=extracted_data.get('purchasingPhone', ''),
            purchasing_email=extracted_data.get('purchasingEmail', ''),
            bid_deadline=extracted_data.get('bidDeadline', ''),
            status='draft',
            document_path=doc_path,
            logo_path=logo_path
        )
        
        db.session.add(record)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Document processed successfully',
            'data': record.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/records', methods=['GET'])
def get_all_records():
    """Get all procurement records"""
    try:
        records = ProcurementRecord.query.order_by(ProcurementRecord.created_at.desc()).all()
        return jsonify({
            'success': True,
            'records': [record.to_dict() for record in records]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/records/<record_id>', methods=['GET'])
def get_record(record_id):
    """Get a specific record"""
    try:
        record = ProcurementRecord.query.filter_by(record_id=record_id).first()
        if not record:
            return jsonify({'error': 'Record not found'}), 404
        
        return jsonify({
            'success': True,
            'record': record.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/records/<record_id>', methods=['PUT'])
def update_record(record_id):
    """Update a record"""
    try:
        record = ProcurementRecord.query.filter_by(record_id=record_id).first()
        if not record:
            return jsonify({'error': 'Record not found'}), 404
        
        data = request.json
        
        # Update fields
        record.title = data.get('title', record.title)
        record.file_no = data.get('fileNo', record.file_no)
        record.ad_dates = data.get('adDates', record.ad_dates)
        record.ship_to_address = data.get('shipToAddress', record.ship_to_address)
        record.vendor_name = data.get('vendorName', record.vendor_name)
        record.remit_to_address = data.get('remitToAddress', record.remit_to_address)
        record.telephone_no = data.get('telephoneNo', record.telephone_no)
        record.federal_tax_id = data.get('federalTaxId', record.federal_tax_id)
        record.authorized_signature = data.get('authorizedSignature', record.authorized_signature)
        record.printed_name = data.get('printedName', record.printed_name)
        record.purchasing_address = data.get('purchasingAddress', record.purchasing_address)
        record.purchasing_contact_name = data.get('purchasingContactName', record.purchasing_contact_name)
        record.purchasing_phone = data.get('purchasingPhone', record.purchasing_phone)
        record.purchasing_email = data.get('purchasingEmail', record.purchasing_email)
        record.bid_deadline = data.get('bidDeadline', record.bid_deadline)
        record.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Record updated successfully',
            'record': record.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/records/<record_id>/approve', methods=['POST'])
def approve_record(record_id):
    """Approve a record"""
    try:
        record = ProcurementRecord.query.filter_by(record_id=record_id).first()
        if not record:
            return jsonify({'error': 'Record not found'}), 404
        
        record.status = 'approved'
        record.approved_at = datetime.utcnow()
        record.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Record approved successfully',
            'record': record.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/records/<record_id>', methods=['DELETE'])
def delete_record(record_id):
    """Delete a record"""
    try:
        record = ProcurementRecord.query.filter_by(record_id=record_id).first()
        if not record:
            return jsonify({'error': 'Record not found'}), 404
        
        # Delete associated files
        if record.document_path and os.path.exists(record.document_path):
            os.remove(record.document_path)
        if record.logo_path and os.path.exists(record.logo_path):
            os.remove(record.logo_path)
        
        db.session.delete(record)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Record deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/records/search', methods=['GET'])
def search_records():
    """Search records"""
    try:
        query = request.args.get('q', '')
        
        records = ProcurementRecord.query.filter(
            db.or_(
                ProcurementRecord.title.ilike(f'%{query}%'),
                ProcurementRecord.file_no.ilike(f'%{query}%'),
                ProcurementRecord.vendor_name.ilike(f'%{query}%')
            )
        ).order_by(ProcurementRecord.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'records': [record.to_dict() for record in records]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Initialize database
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)