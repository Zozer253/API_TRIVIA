import os
from unicodedata import category
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginer_question(request, ma_selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in ma_selection]
    current_question = questions[start:end]

    return current_question

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TERMINÉ: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app)

    """
    @TERMINÉ: Use the after_request decorator to set Access-Control-Allow
    """

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response

    """
    @TERMINÉ:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories')
    def trouver_categories():
        ma_selection = Category.query.all() # Ici je récupère toutes les catégories et le met dans ma_selection
        mes_categories = [categorie.format() for categorie in ma_selection]

        if len(ma_selection) == 0:
            abort(404)
        return jsonify({
            'success': True,
            'categories' : mes_categories
        })


    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions')
    def recuperer_questions():
        ma_selection = Question.query.all()
        cat_courant  = paginer_question(request, ma_selection)
        mes_categories = Category.query.all()

        categories = {category.id:category.type for category in mes_categories}

        if len(cat_courant) == 0:
            abort(404)
        
        # Je retourne un objet json qui sera par la suite envoyé vers le front end
        return jsonify({
            'success': True,
            'questions': cat_courant,
            'total_questions': len(ma_selection),
            'categories':categories,
            'current_category': None
        })





    """
    @TERMINÉ:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    @app.route('/questions/<int:id_question>', methods=['DELETE'])
    def supprimer_question(id_question):
        try:
            questions = Question.query.filter(Question.id == id_question).one_or_none()

            if questions is None:
                abort(400)
            questions.delete()
            Q_selection = Question.query.order_by(Question.id).all()
            C_question  = paginer_question(request, Q_selection)

            return jsonify({
                'success': True,
                'deleted':id_question
            })
        except:
            abort(422)

    """
    @TERMINÉ:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    @app.route('/questions' , methods=['POST'])
    def creer_une_question():
        body = request.get_json()

        N_question = body.get('question',None)
        N_answer = body.get('answer',None)
        N_difficulty = body.get('difficulty',None)
        N_category =body.get('category',None )

        new_object = [N_question, N_answer, N_category, N_difficulty]
        for i in new_object:
            if not i:
                abort(422)

        try:
            question = Question(question=N_question, answer=N_answer, difficulty=N_difficulty,category=N_category)
            question.insert()

            Q_selection = Question.query.order_by(Question.id).all()
            C_question  = paginer_question(request, Q_selection)

            return jsonify({
                'success': True,
                'total_questions':len(Q_selection),
                'Question': C_question
            })

        except:
            abort(422)



    """
    @TERMINÉ:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    @app.route('/questions/recherches' , methods=['POST'])
    def trouver_une_question_specifique():
        body = request.get_json()
        search = body.get('Terme_de_recherche', None)

        try:
            if search:
                selection = Question.query.filter(Question.question.ilike('%{}%'.format(search))).all()
                current_cat = [question.format() for question in selection]
        
                return jsonify({
                'success': True,
                'questions':current_cat,
                'totale_de_questions': len(selection),
                'Ccategory':3
                })

        except:
            abort(422)



    """
    @TERMINÉ:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    mes_categories in the left column will cause only questions of that
    category to be shown.
    """

    @app.route('/categories/<int:id_categorie>/questions')
    def questions_par_categorie(id_categorie):

        try:
            ma_selection = Question.query.filter(Question.category == str(id_categorie)).all()
            mes_categories = [question.format() for question in ma_selection]
            
            return jsonify({
                'success': True,
                'total_de_questions': len(ma_selection),
                'questions':mes_categories,
                'categorie_courante':id_categorie
            })

        except:
            abort(404)



    """
    @TERMINÉ:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    @app.route('/quizzes',methods=['POST'])
    def quiz():
        try:

            body = request.get_json()
            categorie = body.get('quiz_category')
            last_questions = body.get('last_questions')
            if (not 'quiz_category' in body and not 'last_questions' in body):
                abort(422)

            if ( categorie['id']):
                my_questions = Question.query.filter_by(category=categorie['id']).filter(Question.id.notin_((last_questions))).all()
            else:
                my_questions = Question.query.filter(Question.id.notin_((last_questions))).all()
            if len(my_questions) > 0:
                generate_questions = my_questions[random.randrange(0, len(my_questions))].format()
                return jsonify({
                'success': True,
                'question': generate_questions
                })
            else:
                return jsonify({
                    'success': True,
                    'question': None
                })

        except:
            abort(422)
            

    """
    @TERMINÉ:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
        "success": False, 
        "error": 400,
        "message": "bad request"
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
        "success": False, 
        "error": 404,
        "message": "resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
        "success": False, 
        "error": 422,
        "message": "non traetable"
        }), 422

    return app

