1. Create a Virtual Environment with venv

Run the following command in your terminal or command prompt:

`python -m venv venv`

•	python refers to your Python installation. Ensure it’s the version you want to use.
•	venv is the name of the virtual environment folder (you can name it anything).

This creates a self-contained environment in the venv directory.

2. Activate the Virtual Environment

To activate the virtual environment, use the appropriate command based on your operating system:

macOS/Linux: source `venv/bin/activate`
Windows (Command Prompt): `venv\Scripts\activate`
Windows (PowerShell): `.\venv\Scripts\Activate.ps1`

3. Install Packages in the Virtual Environment

With the environment activated, you can install packages using pip:

pip install <package-name>
pip install -r requirements.txt

4. Deactivate the Virtual Environment

When you’re done, deactivate the virtual environment:
`deactivate`

5. Start up the notebook using either

`jupyter lab`
or
`jupyter notebook`




