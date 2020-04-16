import json
from flask import Response, request, url_for
from flask_restful import Resource
from gamescoresapi import db
from jsonschema import validate, ValidationError
from sqlalchemy.exc import IntegrityError
from gamescoresapi.models import Person, Game, Match
from gamescoresapi.constants import *
from gamescoresapi.utils import GamescoresBuilder, create_error_response

class GameCollection(Resource):

    def get(self):
        body = GamescoresBuilder(items=[])
        for game_instance in db.session.query(Game).all():
            item = GamescoresBuilder(
                name=game_instance.name,
                score_type=game_instance.score_type,
            )
            item.add_control(
                "self",
                url_for("api.gameitem", game_id=game_instance.id)
            )
            item.add_control("profile", GAME_PROFILE)
            body["items"].append(item)

        body.add_control("self", url_for("api.gamecollection"))
        body.add_control_add_game()
        body.add_namespace("gamsco", LINK_RELATIONS_URL)

        return Response(
            status=200,
            response=json.dumps(body),
            mimetype=MASON
        )

    def post(self):
        if not request.json:
            return create_error_response(
                    415,
                    "Wrong content type",
                    "Request content type must be JSON"
                )

        try:
            validate(request.json, Game.get_schema())
        except ValidationError as e:
            return create_error_response(
                status_code=400,
                title="Invalid JSON document",
                message=str(e)
            )
        try:
            name = str(request.json["name"])
            score_type = int(request.json["score_type"])
            game_instance = Game(
                name=name,
                score_type=score_type
            )
            db.session.add(game_instance)
            db.session.commit()
        except IntegrityError:
            return create_error_response(
                409,
                "Already exists",
                "Game with name {} already exists".format(name)
            )
        game_instance = db.session.query(Game).filter_by(name=name).first()
        return Response(
            status=201,
            mimetype=MASON,
            headers={
                "Location": str(url_for("api.gameitem", game_id=game_instance.id))
            }
        )


class GameItem(Resource):

    def get(self, game_id):
        game_instance = db.session.query(Game).filter_by(id=game_id).first()
        if game_instance is None:

            return create_error_response(
                status_code=404,
                title="Not found",
                message="game_instance not found"
            )

        body = GamescoresBuilder(
            name=game_instance.name,
            score_type=game_instance.score_type,
        )
        body.add_control("self", url_for("api.gameitem", game_id=game_id))
        body.add_control("profile", GAME_PROFILE)
        body.add_control("gamsco:games-all", url_for("api.gamecollection"))
        body.add_control_edit_game(game_id=game_id)
        body.add_control_delete_game(game_id=game_id)
        body.add_namespace("gamsco", LINK_RELATIONS_URL)
        return Response(response=json.dumps(body), status=200, mimetype=MASON)

    def put(self, game_id):
        game_instance = db.session.query(Game).filter_by(id=game_id).first()

        try:
            validate(request.json, Game.get_schema())
        except ValidationError as e:
            return create_error_response(
                status_code=400,
                title="Invalid JSON document",
                message=str(e)
            )

        if game_instance is None:
            return create_error_response(
                status_code=404,
                title="Unexisting",
                message="The game_instance does not exist"
            )
        try:
            dic = request.json
            game_instance.name = dic["name"]
            game_instance.score_type = dic["score_type"]

        except TypeError:
            return create_error_response(
                status_code=415,
                title="Wrong content type",
                message="Content type should be JSON"
            )

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return create_error_response(
                status_code=409,
                title="Handle taken",
                message="PUT failed due to the  game_instance name being already taken"
            )

        return Response(
            status=204,
            mimetype=MASON
        )

    def delete(self, game_id):
        game_instance = db.session.query(Game).filter_by(id=game_id).first()
        if game_instance is None:

            return create_error_response(
                status_code=404,
                title="Not found",
                message="game_instance not found"
            )
        db.session.delete(game_instance)
        db.session.commit()
        return Response(status=204, mimetype=MASON)