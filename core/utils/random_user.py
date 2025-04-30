import random

from faker import Faker


class RandomUser:
    """
    Utility class to generate random user data with predefined rules.
    Used for positive and negative API test cases.
    """

    def __init__(self):
        """
        Initializes a new random user with:
        - Random gender ("male" or "female")
        - First and last name according to the gender
        - Status with weighted choice: 90% active, 10% inactive
        """
        self._fake = Faker()
        self._gender = random.choice(["male", "female"])
        self._status = random.choices(["active", "inactive"], weights=[90, 10])[0]

        if self._gender == "male":
            self._first_name = self._fake.first_name_male()
            self._last_name = self._fake.last_name_male()
        else:
            self._first_name = self._fake.first_name_female()
            self._last_name = self._fake.last_name_female()

    @property
    def gender(self) -> str:
        """
        :return: The gender of the user ("male" or "female")
        """
        return self._gender

    @property
    def first_name(self) -> str:
        """
        :return: The first name of the user
        """
        return self._first_name

    @property
    def last_name(self) -> str:
        """
        :return: The last name of the user
        """
        return self._last_name

    @property
    def name(self) -> str:
        """
        :return: The full name of the user (first + last name)
        """
        return f"{self.first_name} {self.last_name}"

    @property
    def email(self) -> str:
        """
        :return: A generated email address based on the user's name
        """
        return f"{self.name.replace(' ', '_').lower()}@example.com"

    @property
    def status(self) -> str:
        """
        :return: The user's status ("active" or "inactive")
        """
        return self._status

    def build_user(self, email_value: str) -> dict:
        """
        Builds a user dictionary using the specified email value.

        :param email_value: Email to use in the user dict
        :return: Dict with keys: name, email, gender, status
        """
        return {
            "name": self.name,
            "email": email_value,
            "gender": self.gender,
            "status": self.status,
        }

    @property
    def valid_user(self) -> dict:
        """
        :return: A user dict with valid email and all required fields
        """
        return self.build_user(self.email)

    @property
    def invalid_email_user(self) -> dict:
        """
        :return: A user dict with invalid email (for negative tests)
        """
        return self.build_user("invalid_email")

    @property
    def email_none_user(self) -> dict:
        """
        :return: A user dict with None as email (for negative tests)
        """
        return self.build_user(None)


# Instance used for tests
user = RandomUser()
