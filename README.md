# Grid2Op
[![Downloads](https://pepy.tech/badge/grid2op)](https://pepy.tech/project/grid2op)
[![PyPi_Version](https://img.shields.io/pypi/v/grid2op.svg)](https://pypi.org/project/Grid2Op/)
[![PyPi_Compat](https://img.shields.io/pypi/pyversions/grid2op.svg)](https://pypi.org/project/Grid2Op/)
[![LICENSE](https://img.shields.io/pypi/l/grid2op.svg)](https://www.mozilla.org/en-US/MPL/2.0/)
[![Documentation Status](https://readthedocs.org/projects/grid2op/badge/?version=latest)](https://grid2op.readthedocs.io/en/latest/?badge=latest)
[![circleci](https://circleci.com/gh/BDonnot/Grid2Op.svg?style=shield)](https://circleci.com/gh/BDonnot/Grid2Op)

Grid2Op is a plateform, built with modularity in mind, that allows to perform powergrid operation.
And that's what it stands for: Grid To Operate.
Grid2Op acts as a replacement of [pypownet](https://github.com/MarvinLer/pypownet) 
as a library used for the Learning To Run Power Network [L2RPN](https://l2rpn.chalearn.org/). 

This framework allows to perform most kind of powergrid operations, from modifying the setpoint of generators,
to load shedding, performing maintenance operations or modifying the *topology* of a powergrid
to solve security issues.

Official documentation: the official documentation is available at 
[https://grid2op.readthedocs.io/](https://grid2op.readthedocs.io/).

*   [1 Installation](#installation)
    *   [1.1 Setup a Virtualenv (optional)](#setup-a-virtualenv-optional)
    *   [1.2 Install from source](#install-from-source)
    *   [1.3 Install from PyPI](#install-from-pypi)
    *   [1.4 Install for contributors](#install-for-contributors)
    *   [1.5 Docker](#docker)
*   [2 Main features of Grid2Op](#main-features-of-grid2op)
*   [3 Getting Started](#getting-started)
    *   [0 Basic features](getting_started/0_basic_functionalities.ipynb)
    *   [1 BaseObservation Agents](getting_started/1_Observation_Agents.ipynb)
    *   [2 BaseAction Grid Manipulation](getting_started/2_Action_GridManipulation.ipynb)
    *   [3 Training An BaseAgent](getting_started/3_TrainingAnAgent.ipynb)
    *   [4 Study Your BaseAgent](getting_started/4_StudyYourAgent.ipynb)
*   [4 Documentation](#documentation)
*   [5 Run the tests](#run-the-tests)
*   [6 License information](#license-information)

# Installation
## Requirements:
*   Python >= 3.6

## Setup a Virtualenv (optional)
### Create a virtual environment 
```commandline
cd my-project-folder
pip3 install -U virtualenv
python3 -m virtualenv venv_grid2op
```
### Enter virtual environment
```commandline
source venv_grid2op/bin/activate
```

## Install from source
```commandline
git clone https://github.com/rte-france/Grid2Op.git
cd Grid2Op
pip3 install -U .
cd ..
```

## Install from PyPI
```commandline
pip3 install grid2op
```

## Install for contributors
```commandline
git clone https://github.com/rte-france/Grid2Op.git
cd Grid2Op
pip3 install -e .
pip3 install -e .[test]
pip3 install -e .[docs]
```

## Docker
Grid2Op docker containers are available on [dockerhub](https://hub.docker.com/r/bdonnot/grid2op/tags).

To install the latest Grid2Op container locally, use the following:
```commandline
docker pull bdonnot/grid2op:latest
```

# Main features of Grid2Op
## Core functionalities
Built with modulartiy in mind, Grid2Op acts as a replacement of [pypownet](https://github.com/MarvinLer/pypownet) 
as a library used for the Learning To Run Power Network [L2RPN](https://l2rpn.chalearn.org/). 

Its main features are:
* emulates the behavior of a powergrid of any size at any format (provided that a *backend* is properly implemented)
* allows for grid modifications (active and reactive load values, generator voltages setpoints and active production)
* allows for maintenance operations and powergrid topological changes
* can adopt any powergrid modeling, especially Alternating Current (AC) and Direct Current (DC) approximation to 
  when performing the compitations
* supports changes of powerflow solvers, actions, observations to better suit any need in performing power system operations modeling
* has an RL-focused interface, compatible with [OpenAI-gym](https://gym.openai.com/): same interface for the
  Environment class.
* parameters, game rules or type of actions are perfectly parametrizable
* can adapt to any kind of input data, in various format (might require the rewriting of a class)

## Powerflow solver
Grid2Op relies on an open source powerflow solver ([PandaPower](https://www.pandapower.org/)),
but is also compatible with other *Backend*. If you have at your disposal another powerflow solver, 
the documentation of [grid2op/Backend](grid2op/Backend/Backend.py) can help you integrate it into a proper "Backend"
and have Grid2Op using this powerflow instead of PandaPower.

# Getting Started
Some Jupyter notebook are provided as tutorials for the Grid2Op package. They are located in the 
[getting_started](getting_started) directories. 

These notebooks will help you in understanding how this framework is used and cover the most
interesting part of this framework:

* [0_basic_functionalities](getting_started/0_basic_functionalities.ipynb) covers the basics 
  of reinforcement learning (only the main concepts), how they are implemented in the
  Grid2Op framework. It also covers how to create a valid environment and how to use the 
  `grid2op.main` function to assess how well an agent is performing.
* [1_Observation_Agents](getting_started/1_Observation_Agents.ipynb) details how to create 
  an "expert agent" that will take pre defined actions based on the observation it gets from 
  the environment. This Notebook also covers the functioning of the BaseObservation class.
* [2_Action_GridManipulation](getting_started/2_Action_GridManipulation.ipynb) demonstrates 
  how to use the BaseAction class and how to manipulate the powergrid.
* [3_TrainingAnAgent](getting_started/3_TrainingAnAgent.ipynb) shows how to get started with 
  reinforcement learning in the Grid2Op framework. It will use the code provided by Abhinav Sagar
  available on [his blog](https://towardsdatascience.com/deep-reinforcement-learning-tutorial-with-open-ai-gym-c0de4471f368) 
  or on [his github repository](https://github.com/abhinavsagar/Reinforcement-Learning-Tutorial). This code will
  be adapted (only minor changes, most of them to fit the shape of the data) 
  and a (D)DQN will be trained on this problem.
* [4_StudyYourAgent](getting_started/4_StudyYourAgent.ipynb) shows how to study an BaseAgent, for example
  the methods to reload a saved experiment, or to plot the powergrid given an observation for
  example. This is an introductory notebook. More user friendly graphical interface should
  come soon.

Try them out in your own browser without installing 
anything with the help of mybinder: 
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/rte-france/Grid2Op/master)

# Documentation

Official documentation: the official documentation is available at 
[https://grid2op.readthedocs.io/](https://grid2op.readthedocs.io/).

## Build the documentation
A copy of the documentation can be built if the project is installed *from source*:
you will need Sphinx, a Documentation building tool, and a nice-looking custom
 [Sphinx theme similar to the one of readthedocs.io](https://sphinx-rtd-theme.readthedocs.io/en/latest/):
```commandline
pip3 install -U grid2op[docs]
```
This installs both the Sphinx package and the custom template. Then, the documentation can be built with the command:
```
make html
```
This will create a "documentation" subdirectory and the main entry point of the document will be located at 
[index.html](documentation/html/index.html).

It is recommended to build this documentation locally, for convenience.
For example, the  "getting started" notebooks referenced some pages of the help.

# Run the tests
Provided that Grid2Op is installed *from source*:

## Install additional dependencies
```commandline
pip3 install -U grid2op[test]
```
## Launch tests
```commandline
cd Grid2Op
python3 -m unittest discover
```

# License information
Copyright 2019-2020 RTE France

    RTE: http://www.rte-france.com

This Source Code is subject to the terms of the Mozilla Public License (MPL) v2 also available 
[here](https://www.mozilla.org/en-US/MPL/2.0/)
