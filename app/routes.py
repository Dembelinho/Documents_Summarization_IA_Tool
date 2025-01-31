from flask import Blueprint, render_template, request, flash, current_app, jsonify, redirect, url_for
import os
from werkzeug.utils import secure_filename
from app.document_processor import DocumentProcessor
from app.models import SummaryHistory, db
from datetime import datetime

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
            summary = processor.process_document(filepath, summary_type=summary_type, length=summary_length)

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

    return jsonify({'error': f'Format not supported. Accepted formats : {", ".join(current_app.config["ALLOWED_EXTENSIONS"])}'}), 400


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
