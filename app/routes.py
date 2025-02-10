from io import BytesIO
from flask import Blueprint, render_template, request, flash, current_app, jsonify, redirect, url_for, send_file
import os
from weasyprint import HTML
from werkzeug.utils import secure_filename
from app.document_processor import DocumentProcessor
from app.models import SummaryHistory, db

main = Blueprint('main', __name__)


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


@main.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@main.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part', 'danger')
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    summary_type = request.form.get('summary_type', 'default')
    summary_length = request.form.get('summary_length', 'moderate')  # Default to 3 sentences
    language = request.form.get('language', 'english')

    if file.filename == '':
        flash('No selected file', 'danger')
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        print("File saved  ", filepath, '  --------  ', filename)

        try:
            processor = DocumentProcessor(current_app.config['OPENAI_API_KEY'])
            summary = processor.process_document(filepath, summary_type=summary_type, length=summary_length,
                                                 language=language)

            # Save summary to database
            summary_entry = SummaryHistory(filename=filename, summary_type=summary_type, summary_length=summary_length,
                                           summary_content=summary)
            db.session.add(summary_entry)
            db.session.commit()

            # Clean up the uploaded file
            os.remove(filepath)

            return jsonify({
                'summary': summary,
                'message': 'File processed successfully'
            })
        except Exception as e:
            # Clean up the uploaded file in case of error
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({'error': str(e)}), 500

    return jsonify({
        'error': f'Format not supported. Accepted formats : {", ".join(current_app.config["ALLOWED_EXTENSIONS"])}'}), 400


@main.route('/history')
def history():
    # Retrieve all summaries from the database
    summaries = SummaryHistory.query.order_by(SummaryHistory.created_at.desc()).all()
    return render_template('history.html', summaries=summaries)


@main.route('/delete_summary/<int:summary_id>', methods=['POST'])
def delete_summary(summary_id):
    summary = SummaryHistory.query.get_or_404(summary_id)
    try:
        db.session.delete(summary)
        db.session.commit()
        flash('Summary deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Failed to delete summary.', 'danger')
    return redirect(url_for('main.history'))


@main.route('/delete_all_summaries', methods=['POST'])
def delete_all_summaries():
    try:
        SummaryHistory.query.delete()
        db.session.commit()
        flash('All summaries deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Failed to delete all summaries.', 'danger')
    return redirect(url_for('main.history'))


@main.route('/download_summary/<int:summary_id>', methods=['GET'])
def download_summary(summary_id):
    summary = SummaryHistory.query.get_or_404(summary_id)

    # Create an HTML template for the PDF
    html_content = f"""
    <html>
     <head>
         <title>Summary - {summary.filename}</title>
         <style>
             body {{ font-family: Arial, sans-serif; }}
             h1 {{ color: #007BFF; }}
             .summary-content {{ font-size: 14px; line-height: 1.6; }}
         </style>
     </head>
     <body>
         <h1>Summary of {summary.filename}</h1>
         <p><strong>Type:</strong> {summary.summary_type.capitalize()}</p>
         <p><strong>Length:</strong> {summary.summary_length.capitalize()}</p>
         <p><strong>Created At:</strong> {summary.created_at.strftime('%Y-%m-%d %H:%M:%S')}</p>
         <div class="summary-content">
             {summary.summary_content}
         </div>
     </body>
    </html>
    """
    # Generate PDF from HTML
    pdf = HTML(string=html_content).write_pdf()
    # Create a BytesIO object to hold the PDF
    pdf_buffer = BytesIO(pdf)

    # Return the PDF as a downloadable file
    return send_file(pdf_buffer, as_attachment=True, download_name=f'{summary.filename}_summary.pdf',
                     mimetype='application/pdf')
