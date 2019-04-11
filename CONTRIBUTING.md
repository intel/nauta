# How to contribute to Nauta
Welcome to Nauta project. Now, you are reading the document where process of contributing to repository is described. 
There are a lot of guidelines which are prepared especcially for you. Fell free to be a Nauta developer and help us 
to make our project better.

## Code of conduct
Before you start to contribute top the Nauta, please read first our [Code of Conduct](/CODE_OF_CONDUCT.md) document.

## Reporting bugs
Each software is not free from bugs. When you find a problem in Nauta, please tell us about it. 
Report it using GitHub issues. Before creating an issue you should make sure that problem which you found 
has not been already reported by others. Fill a valid title and clear description. Try to provide more information 
about problem by attaching logs and providing steps to reproduce a problem. Tell us also something about your 
environment: OS, CPU, memory, hard disk size etc.

However, if you encounter on a security vulnerability, please contact with one 
of the core repository contributors directly. It will allow to fix the issue before it is exploited in the wild.

## Documentation
Nauta documentation consists of two areas: [_Installation & Configuration_](/docs/installation-and-configuration) 
and [_User Guide_](/docs/user-guide).

If you have some ideas for documentation improvements or you would like to make our documentation more consistent and 
readable, please help us. Use [_Pull requests_](https://help.github.com/en/articles/about-pull-requests) mechanism for proposing your changes. Anyone can contribute to the Nauta, 
we are happy that we can get help from your side.

## Submitting changes
Contribution process to Nauta repository is based on Github Workflow. There are several steps you should do before 
your changes are merged to the Nauta code.

#### Create a fork
1. Log into your Github account.
2. Go to [https://github.com/intelai/nauta](https://github.com/intelai/nauta)
3. Create fork of nauta repository by clicking on the **Fork** button.

#### Clone a fork to local machine
1. On your developer machine clone a forked repository of Nauta: `git clone https://github.com/{{ your_github_username }}/nauta`.
2. Set upstream do official Nauta repo: `git remote add upstream https://github.com/intelai/nauta`.
3. Block _push_ command for upstream remote: `git remote set-url --push upstream no_push`.
4. Now you should be able to see properly configured remotes: `git remote -v`.

#### Create your branch
1. Enter into the main repository directory.
2. Make sure that you have fresh code: `git fetch upstream`.
3. Set up your base branch: `git checkout develop`.
4. Create your feature branch where you will be developing your changes: `git checkout -b {{ branch_name }}`.

#### Develop and test your changes
When you prepared some code and you think that it is already OK, you should test it. Some of components have integrated
test tools which run unit tests and check styles. Be sure that your code does not break any compatibility and 
all tests pass.

#### Commit your changes and push
Now when your changes are finished, you can commit them using `git commit -a` command.
Next push your changes to the remote: `git push -f {{ your_github_username }} {{ branch_name }}`. 

#### Create a pull request
1. Go to `https://github.com/{{ your_github_username }}/nauta`.
2. Click the `New Pull Request` button.
3. Set up branches, fill the title and clear description, then create a new Pull Request.

#### Review changes
When you creates a new Pull Request, some of Nauta developers will check your changes and give you a feedback. 
If everything is OK, you will be able to merge your changes, if not - then you will do next changes and next Review 
Process will be performed once again.

#### Merge
If a review process is completed with success, you can squash and merge your changes!


## Coding conventions
In Nauta we are using several programming languages and technologies like Python, Javascript, Golang... etc. 
Most of code is written in Python, but deployment scripts use ansible and bash scripting. As a Nauta developer you 
should write the clean code in accordance with the good practices and standards to avoid simple and popular mistakes.

Documentation is written using markup language. More information about syntax you can
find [here](https://guides.github.com/features/mastering-markdown/).
