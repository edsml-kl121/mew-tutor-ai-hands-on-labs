## Key commands

Creates a project
`poetry new project_name`

Installing a dependency
`poetry add requests`

removing a dependency
`poetry remove requests`

installing dependency in dev env.
`poetry add -D notebook`

Adding environments so that it can be used with jupyter notebook.
`poetry run python -m ipykernel install --user --name=demo-project --display-name "Python (demo-project)"`

Installing all dependency (From a second person's perspective)
`poetry install`
or
for dev

`poetry install --without dev`
`poetry install --only dev`