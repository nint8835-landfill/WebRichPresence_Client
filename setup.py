from setuptools import setup, find_packages

setup(
    name="WebRichPresence_Client",
    version="0.1",
    author="Riley Flynn",
    author_email="riley@rileyflynn.me",
    description="Simple command-line client for the WebRichPresence service.",
    packages=find_packages(),
    install_requires=open("requirements.txt").readlines(),
    entry_points={
        "console_scripts": [
            "webrichpresence = WebRichPresence_Client.__main__:run"
        ]
    }
)