import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    # dropdb trivia_test && createdb trivia_test && psql trivia_test < trivia.psql && python3 test_flaskr.py


    def test_get_categories_with_result(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_get_questions_with_result(self):
        res = self.client().get('/questions')
        data = json.loads(res.data) 

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
    
    def test_delete_question_with_result(self):
        res = self.client().delete('/questions/18')
        data = json.loads(res.data) 

        question = Question.query.filter(Question.id==18).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 18)
        self.assertEqual(question, None)

    def test_delete_question_error_404(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data) 

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    def test_create_question_with_result(self):
        res = self.client().post('/questions', json={
            'question': 'test1',
            'answer': 'test1',
            'category': '1',
            'difficulty': '1'
        })
        data = json.loads(res.data) 

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_search_questions_with_result(self):
        res = self.client().post('/questions/search', json={
            'searchTerm': 'what'
        })
        data = json.loads(res.data) 

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_search_questions_with_error_404(self):
        res = self.client().post('/questions/search', json={
            'searchTerm': 'asldfjasdf'
        })
        data = json.loads(res.data) 

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')
    

    def test_get_questions_by_category(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data) 


        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_get_questions_by_category_error_404(self):
        res = self.client().get('/categories/123/questions')
        data = json.loads(res.data) 

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_play_quiz_with_result(self):
        res = self.client().post('/quizzes', json={
            'previous_questions': '1',
            'quiz_category': {
                'type': 'History',
                'id': 4
            }
        })
        data = json.loads(res.data) 

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_play_quiz_error_422(self):
        res = self.client().post('/quizzes', json={
            'previous_questions': '1',
            'quiz_category': {
                'type': 'History',
            }
        })
        data = json.loads(res.data) 

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable') 
    

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
