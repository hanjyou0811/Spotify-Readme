from flask import Flask, Response, redirect
from requests.exceptions import RequestException

from spotify_readme.modules.environment_variables import ENV_VARS
from spotify_readme.modules.functions import SpotifyAPI, make_link_page, make_svg_widget


def create_app() -> Flask:
    app: Flask = Flask(__name__)

    @app.route("/now")
    def now() -> Response:
        """Open the current track, or the most recently played track, in Spotify."""
        url = "https://open.spotify.com/"
        spotify_api = SpotifyAPI(
            client_id=ENV_VARS.CLIENT_ID,
            client_secret=ENV_VARS.CLIENT_SECRET,
            refresh_token=ENV_VARS.REFRESH_TOKEN,
        )
        try:
            current = spotify_api.make_request("me/player/currently-playing")
            track = current.get("item")
            if not track:
                recent = spotify_api.make_request("me/player/recently-played?limit=1")
                items = recent.get("items") or []
                track = items[0].get("track") if items else None
            if track and track.get("id"):
                url = f"https://open.spotify.com/track/{track['id']}"
        except (RequestException, ValueError):
            app.logger.warning("Could not retrieve the Spotify track for /now")
        resp = redirect(url, code=302)
        resp.headers["Cache-Control"] = "no-store"
        return resp

    # @app.route("/link")
    # def link() -> Response:
    #     """Display setup instructions as well as the current song."""
    #     resp: Response = Response(
    #         response=make_link_page(),
    #         mimetype="text/html",
    #     )
    #     resp.headers["Cache-Control"] = "s-maxage=1"  # Cache for 1 second
    #     resp.headers["Access-Control-Allow-Origin"] = "*"  # Allow all origins
    #     return resp

    @app.route(rule="/", defaults={"path": ""})
    @app.route(rule="/<path:path>")
    def catch_all(path: str) -> Response:
        """Catch all requests and return the rendered SVG."""
        resp: Response = Response(
            response=make_svg_widget(track_id=path),
            mimetype="image/svg+xml",
        )
        resp.headers["Cache-Control"] = "s-maxage=1"  # Cache for 1 second
        resp.headers["Access-Control-Allow-Origin"] = "*"  # Allow all origins
        return resp

    return app


app: Flask = create_app()  # Created in global scope for PythonAnywhere


def main() -> None:
    app.run(debug=True)


if __name__ == "__main__":
    main()
