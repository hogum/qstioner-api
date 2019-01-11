"""
    This module contains resource views for the
    rsvp Resource
"""

from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.v1.models.rsvp import RsvpModel
from ..models.meetups import MeetUpModel
from ..models.users import UserModel


class Rsvps(Resource):

    @jwt_required
    def post(self, id, response):
        """
            Creates an rsvp with refrence to a meetup and the
            existing user's
        """

        args = {}

        # Confirm response is valid

        ex = ['yes', 'no', 'maybe']

        err_msg = "Your response is not known. Make it: " + \
            str(ex[:-1]) + ' or ' + str(ex[-1])

        if response not in ex:
            return {
                "Status": 400,
                "Message": err_msg
            }

        # Confirm existence of the meetup  to rsvp

        if not MeetUpModel.get_by_id(id):
            return {
                "Status": 404,
                "Message": "That meetup does not exist"
            }, 404

        user = UserModel.get_by_name(get_jwt_identity())

        user_id = getattr(user, 'id')

        args.update({
            "user": user_id,
            "meetup": id,
            "response": response
        })

        # Create rsvp and confirm it's not a duplicate

        rsvp = RsvpModel(**args)
        if not RsvpModel.verify_unique(rsvp):
            return {
                "Status": 409,
                "Message": "You've done that same rsvp already"
            }, 409
        rsvp.save()

        return {
            "Status": 201,
            "Data": rsvp.dictify()
        }, 201
