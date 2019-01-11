from .base_test import BaseTestCase


class RSVPTest(BaseTestCase):

    def test_create_new_rsvp(self):

        response = self.post('api/v1/meetups/1/yes')

        self.assertEqual(response.status_code, 201,
                         msg="Fails to rsvp for a meetup")

    def test_create_rsvp_with_unknown_response(self):
        # Known responses are 'yes', 'no' and 'maybe'

        response = self.post('api/v1/meetups/1/so')
        self.assertTrue("Your response is not known"
                        in response.get_json().get("Message"),
                        msg="Fails to not\
                         create an rsvp with an invalid response")

    def test_rsvp_for_nonexistent_meetup(self):
        res = self.post('api/v1/meetups/500/no')

        res_msg = res.get_json().get('Message')

        self.assertEqual(res_msg, "That meetup does not exist",
                         msg="Fails to not rsvp a missing meetup")
