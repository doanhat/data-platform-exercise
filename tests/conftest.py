def pytest_addoption(parser):
    parser.addoption("--bucket", action="store", default="test-bucket")
    parser.addoption("--runner", action="store", default="DirectRunner")
    parser.addoption("--date", action="store")
