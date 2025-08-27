import os

from flask import Flask
from src.gen.chain import create_graph


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize graph
    graph = create_graph()
    # runnable = graph.with_types(input_type=ChatInputType, output_type=dict)

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        initial_state = {"messages": [("user", "Give me daily Apple stock prices")]}
        out = graph.invoke(initial_state, config={"configurable": {"thread_id": "1"}})
        # out = graph.invoke("Give me daily IBM stock prices")
        print(out["messages"][-1])
        return str(out["messages"][-1].content)

    return app