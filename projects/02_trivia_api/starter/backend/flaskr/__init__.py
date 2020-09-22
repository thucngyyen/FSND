import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''

  CORS(app)

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''

  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

  '''
  Paginate method
  '''
  
  def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page-1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''

  @app.route('/categories', methods=['GET']) 
  def retrieve_categories():
    try:
      # Retrieve cate and then format it
      categories = Category.query.order_by(Category.id).all()
      current_categories = {category.id: category.type for category in categories}
      
      # Check if there is any category in database
      if not len(current_categories):
        abort(404) 
      
      # Return
      return jsonify({
        'success': True,
        'categories': current_categories,
        'total_categories': len(current_categories)
      })
    except:
      abort(422)

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''

  @app.route('/questions', methods=['GET'])
  def retrieve_questions():
    try:
      # Retrieve all ques and cate, sort by id
      questions = Question.query.order_by(Question.id).all()
      categories = Category.query.order_by(Category.id).all()

      # Format and paginate before returning
      current_questions = paginate_questions(request, questions)
      current_categories = {category.id: category.type for category in categories}
      
      # Check if there is any question 
      if not len(questions):
        abort(404) 

      # Return
      return jsonify({
        'success': True,
        'questions': current_questions,
        'total_questions': len(questions),
        'current_category': None,
        'categories': current_categories
      })
    except:
      abort(422)

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''

  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      # Retrieve the question with given id
      question = Question.query.filter(Question.id==question_id).one_or_none()
      
      # Check if there such a question 
      if question is None:
        abort(404)
      
      # Question exists, deleting:
      question.delete()
      selection = Question.query.order_by(Question.id).all()
      current_questions = paginate_questions(request, selection)

      # Return 
      return jsonify({
        'success': True,
        'deleted': question_id,
        'questions': current_questions,
        'total_questions': len(Question.query.all())
      })
    except:
      abort(422)

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''

  @app.route('/questions', methods=['POST'])
  def create_question():
    # Request new agrs for new question
    body = request.get_json()
    new_question = body.get('question', None)
    new_answer = body.get('answer', None)
    new_category = body.get('category', None)
    new_difficulty = body.get('difficulty', None)

    try:
      # Add new question
      question = Question(question=new_question, answer=new_answer, 
                          category=new_category, difficulty=new_difficulty)
      question.insert()
      
      # Paginate 
      selection = Question.query.order_by(Question.id).all()
      current_question = paginate_questions(request, selection)

      # Returning
      return jsonify({
        'success': True,
        'created': question.id,
        'questions': current_question,
        'total_questions': len(Question.query.all())
      })
    except: 
      abort(422)

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

  @app.route('/questions/search', methods=['POST'])
  def search_question():
    # Request new args for searchTerm
    body = request.get_json()
    search_term = body.get('searchTerm', None)
    
    # Search by searchTerm (case insensitive)
    selection = Question.query.order_by(Question.id).filter(
                Question.question.ilike('%{}%'.format(search_term)))

    # Check if any question contains searchTerm
    if not selection.count():
      abort(404)

    # Paginate
    current_questions = paginate_questions(request, selection)

    #Return
    return jsonify({
      'success': True,
      'questions': current_questions, 
      'total_questions': len(selection.all()),
      'current_category': None
    })
    
  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''

  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def retrieve_questions_by_category(category_id):
    # Get all questions in the given category
    selection = Question.query.filter_by(category=str(category_id)).all()
    current_questions = [question.format() for question in selection]

    # Check if any questions in that category
    if not len(current_questions):
      abort(404)

    # Returning
    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': len(current_questions),
      'current_category': str(category_id)
    })


  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''

  @app.route('/quizzes', methods=['POST'])
  def start_quiz():
    
    try:
      # Request previous_questions and quiz_category
      body = request.get_json()
      previous_questions = body.get('previous_questions', [])
      quiz_category = body.get('quiz_category', None)

      # If quiz_category is included
      if quiz_category:
        # If previous_questions exist
        if "previous_questions" in body and len(previous_questions) > 0:
          # Previous_questions exist as well as category
          questions_list = Question.query.filter(Question.id.notin_(previous_questions),
                            Question.category==str(quiz_category['id'])).all()
        else:#If previous_questions dont exist
          # Category includes but not previous_questions
          questions_list = Question.query.filter(
                            Question.category==str(quiz_category['id'])).all()

      else:#If category is NOT included
        #If previous_questions exists
        if "previous_questions" in body and len(previous_questions) > 0:
          # Previous_questions exist but not category
          questions_list = Question.query.filter(
                            Question.id.notin_(previous_questions)).all()
        else:#Previous_questions isn't
          # Non included
          # By default, this will be the ALL selection
          questions_list = Question.query.all()
      
      # Format before returning
      selections = [selection.format() for selection in questions_list]
      
      # Check if there is actually any question 
      if len(selections):

        question = random.choice(selections)
        
        result = {
          'success': True,
          'question': question,
          'asdf': quiz_category['id']
        }

      else:
        
        result = {
          'success': False,
          'question': None
        }, 404
        
      #Return
      return jsonify( result )

    except:
      abort(422)

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      'success': False,
      'error': 400,
      'message': 'bad request, check your syntax'
    }), 400

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success': False, 
      'error': 404,
      'message': 'resource not found'
      }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      'success': False, 
      'error': 422,
      'message': 'unprocessable'
      }), 422

  @app.errorhandler(500)
  def server_error(error):
    return jsonify({
      'success': False,
      'error': 500,
      'message': 'internal server error'
    }), 500

  return app

    