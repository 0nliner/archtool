from setuptools import setup, find_packages


setup(
        name='injector',
        version='0.1',
        license='MIT',
        author="Aleksandr Chudaikin",
        author_email='aleksandrchudaikindev@gmail.com',
        # packages=find_packages(exclude=['src/tests']),
        package_dir={'': 'injector'},
        url='https://github.com/0nliner/injector',
        keywords='',

        install_requires=[],

        classifiers=[
            'Development Status :: 3 - Alpha',

            # Indicate who your project is intended for
            'Intended Audience :: DevOps',
            'Topic :: Software Development :: DevOps',

            # Pick your license as you wish (should match "license" above)
            'License :: OSI Approved :: MIT License',

            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9',
        ],
        python_requires='>=3.8',

        entry_points={
            'console_scripts': [
                'sample=sample:main',
            ],
        },
)