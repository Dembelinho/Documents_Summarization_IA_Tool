from datetime import datetime
from app import db


class SummaryHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)
    summary_type = db.Column(db.String(50), nullable=False)
    summary_length = db.Column(db.String(50), nullable=False)
    summary_content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<SummaryHistory {self.filename}>"
