import os
import sys

if not __package__:
    # Make CLI runnable from source tree with
    #    python src/ebms_analytics
    package_source_path = os.path.dirname(os.path.dirname(__file__))
    sys.path.insert(0, package_source_path)

if __name__ == "__main__":
    from ebms_analytics.app import app
    app()
