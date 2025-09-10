from airflow.plugins_manager import AirflowPlugin
from flask import Blueprint

# Define a Flask Blueprint for your static files
my_theme_bp = Blueprint(
    "my_theme_plugin",
    __name__,
    static_folder="static",
    static_url_path="/my_theme_plugin/static",
)

# Define the plugin
class MyThemePlugin(AirflowPlugin):
    name = "my_theme_plugin"
    flask_blueprints = [my_theme_bp]
