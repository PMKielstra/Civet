import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="civet-runner",
    version="1.0.0",
    author="Michael Kielstra",
    author_email="just-file-a-github-issue@fakeemail.com",
    description="Civet: software to run the same program multiple times with different arguments",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/PMKielstra/Civet",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6'
)
