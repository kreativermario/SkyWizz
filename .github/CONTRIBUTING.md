# Contribution Standards
Don't be afraid to contribute to the development of SkyWizz! Even if you don't think you've contributed much, it's still greatly appreciated.

Please make sure you abide by these contribution standards so we can retain a high quality codebase and make it easy for everyone to understand and contribute to the code.

* Follow all coding standards set by existing code in the repo. Using your own preferences over the established ones for the project just ends up making the code messy.
* Use commits following our guidelines [here](#commit-messages).
* An explanation of what the commit's changes do in your commit message is extremely useful. It helps people to more quickly understand what your code is doing.
* When you submit a pull request, be willing to accept criticism. We don't criticise to make you feel bad - we want you to know where you may have made a mistake and this helps you grow as a developer.

## How to start to contribute

1. Fork the repository to your own GitHub account.
2. Clone the project to your local machine.
3. Create a branch locally with a succinct but descriptive name.
4. Work on the feature or bug.
5. Commit changes in small, incremental steps.
6. Push your branch to your forked repository.
7. Make a pull request from your forked repository to the main repository.
8. Have a discussion with the maintainers about the changes.

## Commit messages

We use [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) for our commit messages, which provides a standardized format for describing the changes made in a commit. 

A commit message should have the following format:

type(scope): subject

type: The type of change being made (e.g. feat, fix, docs, style, refactor, test, chore).
scope (optional): The scope of the change (e.g. filename, module, package, etc.).
subject: A brief description of the change.
body (optional): A more detailed description of the change.
footer (optional): A section for any related issue numbers or breaking changes.

  
Here are some examples:

```csharp
feat(api): add new endpoint for getting airport distance
```
```scss
fix(gui): resolve issue with button not displaying correctly
 ```
```sql
docs: update README with new screenshots
```
 

## Code Style
  
We use PEP 8 guidelines for Python code style. Please ensure your code follows these guidelines.

## Documentation

We follow Google style for documentation.

Here is an example:
```python
def add(a: Union[float, int], b: Union[float, int]) -> float:
    """Compute and return the sum of two numbers.

    Examples:
        >>> add(4.0, 2.0)
        6.0
        >>> add(4, 2)
        6.0

    Args:
        a (float): A number representing the first addend in the addition.
        b (float): A number representing the second addend in the addition.

    Returns:
        float: A number representing the arithmetic sum of `a` and `b`.
    """
    return float(a + b)
```

# Filing an Issue
We always encourage users to report bugs as soon as they experience them. In order to keep everything organized here are some questions you should ask yourself before reporting:

## Common mistakes
* Have you followed everything on <https://kreativermario.github.io/SkyWizz/user-guide/installation/>?
* Have you set up your environment variables (.env)? Run the SkyWizz.py to set them up.
* Do you have all the dependencies installed and properly configured?

## General issues
* Are you using the latest version of SkyWizz?
* Has this issue been reported already? Please check the [list of open issues](https://github.com/kreativermario/SkyWizz/issues).

## Advice
If you're sure you've followed all instructions and haven't made any of the common mistakes listed above, here are some guidelines for creating an issue:

* Is this an issue with SkyWizz itself, or a compiler error, or are you looking for help with your code? The SkyWizz issues page is for SkyWizz issues only. Try the [GitHub Discussions tab](https://github.com/kreativermario/SkyWizz/discussions).
* When you ask a question, make sure it's not [an XY problem](http://xyproblem.info/).
* Provide as much information as you possibly can.
* Issues are formatted by [Markdown](https://guides.github.com/features/mastering-markdown/). If you paste code into your issue, it will probably end up appearing quite broken because it was interpreted as Markdown. Enclose blocks of code with three backticks (\`\`\`) at the start and end to make it a nicely formatted code block.

## In your issue, please:
* List all operating system names and versions involved in the issue, as well as the IDE, Python version and dependencies version.
* List any other software name/version you think may be related.
* Include any error messages you see.
* List steps to reproduce.

The more information you have, the better. Post as much as you can related to the issues to help us resolve it in a timely matter. If you have multiple issues, please file them as separate issues. This will help us sort them out efficiently.

Don't ask a question not related to the topic of the current issue, especially if it's on someone else's issue. This is known as [thread hijacking](http://www.urbandictionary.com/define.php?term=Thread+Hijacking). You should create a new issue, or ask on another discussion forum. To contact a specific developer, find their GitHub profile and look for their email address, etc.

Thanks!


