from setuptools import find_packages, setup

setup(
    name="the-littlest-jupyterhub",
    version="2.0.1.dev",
    description="A small JupyterHub distribution",
    url="https://github.com/jupyterhub/the-littlest-jupyterhub",
    author="Jupyter Development Team",
    author_email="jupyter@googlegroups.com",
    license="3 Clause BSD",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.9",
    install_requires=[
        "ruamel.yaml",
        "jinja2",
        "pluggy",
        "backoff",
        "filelock",
        "requests",
        "bcrypt",
        "jupyterhub-traefik-proxy",
    ],
    entry_points={
        "console_scripts": [
            "tljh-config = tljh.config:main",
        ]
    },
)
