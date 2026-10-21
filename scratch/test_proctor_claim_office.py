import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from system.database import get_proctor_exams, open_db, is_schedule_published, publish_schedule, unpublish_schedule
from system.exporter import export_proctor_duty_slip_pdf

class TestProctorClaimOffice(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_database_claim_office_resolution(self):
        """Verify get_proctor_exams provides offering_institute_code and claim_office"""
        db = open_db()
        c = db.cursor(dictionary=True)
        c.execute("""
            SELECT e.instructor_id, COUNT(*) as cnt 
            FROM exams e 
            WHERE e.instructor_id IS NOT NULL AND e.status = 'Scheduled' AND e.exam_date_time IS NOT NULL 
            GROUP BY e.instructor_id 
            HAVING cnt > 0 
            LIMIT 1
        """)
        row = c.fetchone()
        db.close()

        self.assertIsNotNone(row, "Should find at least one scheduled proctor")
        inst_id = row['instructor_id']

        exams = get_proctor_exams(inst_id)
        self.assertGreater(len(exams), 0, "Proctor should have exams")

        for exam in exams:
            self.assertIn('offering_institute_code', exam)
            self.assertIn('claim_office', exam)
            self.assertTrue(len(exam['claim_office']) > 0)
            if exam['offering_institute_code'] == 'ICSLIS':
                self.assertEqual(exam['claim_office'], "ICSLIS Dean's / Secretary Office")
            elif exam['offering_institute_code'] == 'IBM':
                self.assertEqual(exam['claim_office'], "IBM Dean's / Secretary Office")
            elif exam['offering_institute_code'] == 'IEAS':
                self.assertEqual(exam['claim_office'], "IEAS Dean's / Secretary Office")

    def test_proctor_dashboard_html_rendering_published(self):
        """Verify the proctor dashboard HTML includes the Claim Test Papers indicator badge when published"""
        with self.client.session_transaction() as sess:
            sess['user_id'] = 5
            sess['instructor_id'] = 802
            sess['role'] = 'proctor'
            sess['full_name'] = 'Andes, Arbien Paulo E.'

        initially_published = is_schedule_published()
        publish_schedule()
        try:
            response = self.client.get('/proctor')
            self.assertEqual(response.status_code, 200)
            html = response.get_data(as_text=True)

            self.assertIn('Claim Test Papers At:', html)
            # Jinja HTML escapes apostrophe to &#39;
            self.assertTrue("ICSLIS Dean&#39;s / Secretary Office" in html or "ICSLIS Dean's / Secretary Office" in html)
            self.assertTrue("IBM Dean&#39;s / Secretary Office" in html or "IBM Dean's / Secretary Office" in html)
            self.assertTrue("IEAS Dean&#39;s / Secretary Office" in html or "IEAS Dean's / Secretary Office" in html)
            self.assertIn('fa-box-archive', html)
            print("Verified: Claim badges for ICSLIS, IBM, IEAS all render in Proctor Dashboard HTML!")
        finally:
            if not initially_published:
                unpublish_schedule()

    def test_proctor_duty_slip_pdf_generation(self):
        """Verify the proctor PDF duty slip generates cleanly with claim office"""
        exams = get_proctor_exams(802)
        pdf_bytes = export_proctor_duty_slip_pdf(
            proctor_name='Andes, Arbien Paulo E.',
            exams=exams,
            exam_term='Midterm',
            exam_semester='1st Semester',
            total_hours=len(exams) * 1.5
        )
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertGreater(len(pdf_bytes), 1000)
        self.assertTrue(pdf_bytes.startswith(b'%PDF'), "Output must be valid PDF header")
        print(f"Verified: Proctor Duty Slip PDF generated successfully ({len(pdf_bytes)} bytes)")

if __name__ == '__main__':
    unittest.main()
