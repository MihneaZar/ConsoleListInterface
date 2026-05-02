from setuptools import setup

setup(
    name='ConsoleListInterface',
    version='0.1.0',    
    description='Simple console interface for interacting with a dynamic list',
    url='https://github.com/MihneaZar/ConsoleListInterface',
    author='Mihnea Bogdan Zarojanu',
    author_email='mihneabogzar@gmail.com',
    license='MIT',
    packages=['ConsoleListInterface'],
    install_requires=['readchar>=4.2.1',
                      'cursor>=1.3.5',                     
                      ],

    classifiers=[
        'License :: OSI Approved :: MIT License',         
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)