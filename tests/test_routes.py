import unittest
from unittest.mock import patch
import os
from app.document_processor import DocumentProcessor
from flask import Flask
from flask_testing import TestCase
from app import create_app, db
from app.models import SummaryHistory
from app.routes import main


class TestRoutes(TestCase):
    def create_app(self):
        # Configure the app for testing
        app = create_app()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), "test_uploads")
        app.config['WTF_CSRF_ENABLED'] = False
        return app

    def setUp(self):
        # Create the upload folder
        os.makedirs(self.app.config['UPLOAD_FOLDER'], exist_ok=True)

        # Initialize the database
        db.create_all()

    def tearDown(self):
        # Clean up the upload folder
        for file in os.listdir(self.app.config['UPLOAD_FOLDER']):
            os.remove(os.path.join(self.app.config['UPLOAD_FOLDER'], file))
        os.rmdir(self.app.config['UPLOAD_FOLDER'])

        # Drop the database
        db.session.remove()
        db.drop_all()

    def test_index_route(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Document Summarizer", response.data)

    def test_upload_file_valid(self):
        # Create a test file
        test_file = os.path.join(self.app.config['UPLOAD_FOLDER'], "test.txt")
        with open(test_file, "w") as f:
            f.write("This is a test file.")

        # Mock the DocumentProcessor
        with patch.object(DocumentProcessor, 'process_document', return_value="Mock summary"):
            with open(test_file, "rb") as f:
                response = self.client.post('/upload', data={
                    'file': f,
                    'summary_type': 'default',
                    'summary_length': 'concise',
                    'language': 'english'
                })

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Mock summary", response.data)

    def test_upload_file_invalid_format(self):
        # Create an unsupported file
        test_file = os.path.join(self.app.config['UPLOAD_FOLDER'], "test.unsupported")
        with open(test_file, "w") as f:
            f.write("This is an unsupported file.")

        # Mock the file upload
        with open(test_file, "rb") as f:
            response = self.client.post('/upload', data={
                'file': f,
                'summary_type': 'default',
                'summary_length': 'concise',
                'language': 'english'
            })

        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Format not supported", response.data)

    def test_history_route(self):
        # Add a test summary to the database
        summary = SummaryHistory(
            filename="test.txt",
            summary_type="default",
            summary_length="concise",
            summary_content="Mock summary"
        )
        db.session.add(summary)
        db.session.commit()

        response = self.client.get('/history')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"test.txt", response.data)

    def test_delete_summary(self):
        # Add a test summary to the database
        summary = SummaryHistory(
            filename="test.txt",
            summary_type="default",
            summary_length="concise",
            summary_content="Mock summary"
        )
        db.session.add(summary)
        db.session.commit()

        response = self.client.post(f'/delete_summary/{summary.id}')
        self.assertEqual(response.status_code, 302)  # Redirect to history page
        self.assertEqual(SummaryHistory.query.count(), 0)


if __name__ == "__main__":
    unittest.main()