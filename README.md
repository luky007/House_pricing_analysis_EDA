> [!NOTE]  
> This project is part of a dummy simulation.

# Final project - House pricing analysis

Collection of scripts for cleaning and analyzing the input dataset related to the housing market.

## How to contribute:
### Using docker container
- Open this project inside a docker container. The use of VS code dev containers is encouraged.
- Initialize the project dependencies by using Poetry:
```bash
poetry install --no-root
```

### Manual install
- Setup the conda environment with:
```bash
conda env create -f environment.yml
```
- Then initialize the project dependencies by using Poetry:
```bash
poetry install --no-root
```

## How to execute jupyter notebook:
- Activate the installed poetry env with:
```bash
poetry shell
```
- Then run jupyterlab. The use of mrx-link plugin is encouraged.
```bash
jupyter-lab --allow-root
```