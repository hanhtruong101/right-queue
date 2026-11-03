import os

from locust import HttpUser, between, task


class RightQueueRequester(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        self.username = os.environ.get("LOAD_TEST_USERNAME")
        self.password = os.environ.get("LOAD_TEST_PASSWORD")
        self.organization_slug = os.environ.get(
            "ORGANIZATION_SLUG",
            "fontys",
        )

        if not self.username or not self.password:
            raise RuntimeError(
                "LOAD_TEST_USERNAME and LOAD_TEST_PASSWORD must be set."
            )

        csrf_token = self._get_csrf_token()

        login_response = self.client.post(
            "/api/auth/login/",
            json={
                "username": self.username,
                "password": self.password,
            },
            headers={
                "X-CSRFToken": csrf_token,
            },
            name="POST /api/auth/login/",
        )

        if login_response.status_code != 200:
            raise RuntimeError(
                "Performance-test login failed."
            )

        # Django rotates the CSRF token after a successful login.
        self.csrf_token = self._get_csrf_token()

    def _get_csrf_token(self):
        response = self.client.get(
            "/api/auth/csrf/",
            name="GET /api/auth/csrf/",
        )

        if response.status_code != 200:
            raise RuntimeError(
                "Could not retrieve a CSRF token."
            )

        try:
            response_data = response.json()
        except ValueError as error:
            raise RuntimeError(
                "The CSRF endpoint did not return valid JSON."
            ) from error

        csrf_token = response_data.get("csrf_token")

        if not csrf_token:
            raise RuntimeError(
                "The CSRF response did not contain csrf_token."
            )

        return csrf_token

    @task(5)
    def list_my_requests(self):
        with self.client.get(
            (
                f"/api/organizations/"
                f"{self.organization_slug}/requests/"
            ),
            name="GET /api/organizations/:slug/requests/",
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(
                    f"Expected HTTP 200, received "
                    f"{response.status_code}."
                )
                return

            try:
                response_data = response.json()
            except ValueError:
                response.failure(
                    "My Requests did not return valid JSON."
                )
                return

            if not isinstance(response_data, list):
                response.failure(
                    "My Requests did not return a JSON list."
                )
    @task(4)
    def list_services(self):
        with self.client.get(
            (
                f"/api/organizations/"
                f"{self.organization_slug}/services/"
            ),
            name="GET /api/organizations/:slug/services/",
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(
                    f"Expected HTTP 200, received "
                    f"{response.status_code}."
                )
                return

            try:
                response_data = response.json()
            except ValueError:
                response.failure(
                    "The service catalogue did not return valid JSON."
                )
                return

            if not isinstance(response_data, list):
                response.failure(
                    "The service catalogue did not return a JSON list."
                )