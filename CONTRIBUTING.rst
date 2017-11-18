============
Contributing
============

Contributions are welcome, and they are greatly appreciated! Every
little bit helps, and credit will always be given.

You can contribute in many ways:

Types of Contributions
----------------------

Report Bugs
~~~~~~~~~~~

Report bugs at usrolh@tdstelecom.com

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

Fix Bugs
~~~~~~~~

Look through the Gitlab or JIRA issues for bugs. Feel free to snag
anything not currently being worked on.

Implement Features
~~~~~~~~~~~~~~~~~~

Look through the Gitlab or JIRA issues for features. Feel free to snag
anything not currently being worked on.

Write Documentation
~~~~~~~~~~~~~~~~~~~

tdsnmp could always use more documentation, whether as part of the
official project docs, in docstrings, or even on a team Wiki or Sharepoint.

Submit Feedback
~~~~~~~~~~~~~~~

The best way to send feedback is to email usrolh@tdstelecom.com.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions
  are welcome :)

Get Started!
------------

Ready to contribute? Here's how to set up `tdsnmp` for local development.

1. Fork the `tdsnmp` repo on Gitlab.
2. Clone your fork locally::

    $ git clone git@git.ent.tds.net:usrolh/tdsnmp.git

3. Install your local copy into a virtualenv. Assuming you have virtualenvwrapper installed, this is how you set up your fork for local development::

    $ mkvirtualenv dev-tdsnmp
    $ cd tdsnmp/
    $ python setup.py develop

4. Create a branch for local development::

    $ git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally.

5. When you're done making changes, check that your changes pass flake8 and the tests, including testing other Python versions with tox::

    $ python setup.py test

6. Commit your changes and push your branch to Gitlab::

    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature

7. Submit a merge request through the Gitlab website.

Merge Request Guidelines
-----------------------

Before you submit a merge request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring, and add the
   feature to the list in README.rst.
3. The pull request should work for Python 2.7+, and 3.4+, and for PyPi.

Tips
----

To run a subset of tests::

    $ python -m unittest tests.tdsnmp.test_tdsnmp
