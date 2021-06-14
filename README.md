# Ant Colony Power Systems Optimizer

This library aims to provide a tool to obtain an optimal dispach of a Power System comprised of Thermal Generation Units. The approach combines the Ant Colony Optimizer with a non-linear solver provided by CVXOPT.

> This is an under development library

## Installation instructions

### PyPi
A pre-built binary wheel package can be installed using pip:
```sh
pip install acopoweropt
```

### Poetry
Poetry is a tool for dependency management and packaging in Python. `acopoweropt` can be installed in a poetry managed project:
```sh
poetry add acopoweropt
```

## Usage
From a domain perspective, there should be a complete decoupling between an Ant Colony and a Power System, after all ants do not have knowledge of power systems. Therefore an initial approach was to develop to main _Entities_: A `Colony` and a `Power System`. A Power System should be solved by a mathematical method 

## License

See the [LICENSE](LICENSE.md) file for license rights and limitations (MIT).