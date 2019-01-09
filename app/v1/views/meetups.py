from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
import datetime

from app.v1.models.meetups import MeetUpModel
from app.v1.utils.helpers import admin_required


class Meetups(Resource):
    """
        This resource allows an admin user to create a meetup.
        It also makes it possible for any user to fetch all existing meetups
    """
    @jwt_required
    @admin_required
    def post(self):
        parser = reqparse.RequestParser(trim=True, bundle_errors=True)
        parser.add_argument('topic', type=str)
        parser.add_argument(
            'happeningOn',
            type=lambda t: datetime.strptime(t, '%Y-%m-%dT%H:%M:%S'),
            default=datetime.datetime.utcnow().isoformat())
        parser.add_argument('tags', type=str, action='append')
        parser.add_argument('location', type=str)
        parser.add_argument('images', type=str, action='append')

        args = parser.parse_args(strict=True)

        # Ensure a meetup isn't created with same data twice

        new_meetup = MeetUpModel(**args)

        if MeetUpModel.verify_unique(new_meetup):
            return {
                "Status": 409,
                "Message": "Relax, Meetup already created"
            }, 409

        new_meetup.save()

        return {
            "Status": 201,
            "Data": [new_meetup.dictify()]
        }


class MeetUp(Resource):
    """
        This resource fetches all existing meetup records
    """

    def get(self):

        return {
            "Status": 200,
            "Data": [MeetUpModel.get_all_meetups()]
        }


class MeetUpItem(Resource):
    """
        Searches for a meetup by its id
        and returns a matching record.
    """

    def get(self, id):

        if not MeetUpModel.get_by_id(id):
            return {
                "Status": 404,
                "Error": "Meetup non-existent"
            }
        return {
            "Status": 200,
            "Data": [MeetUpModel.get_by_id(id)]
        }
