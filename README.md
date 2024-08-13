# How to use

## Set up git credential for your device
> When you access a repository using Git on the command line using commands like git clone, git fetch, git pull or git push with HTTPS URLs, you must provide your GitHub username and your personal access token when prompted for a username and password. The command line prompt won't specify that you should enter your personal access token when it asks for your password.

1. [Generate a Personal Access Token](https://github.com/settings/tokens)([details](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens))
2. Copy the Personal Access Token.
3. Re-attempt the command you were trying and use Personal Access Token in the place of your password.


## Set up the repo on your device

```markdown
git clone <repository-url> // use HTML url
cd <repository-name>
git checkout -b feature-branch

// make your changes
git add .
git commit -m "Your commit message"
git push -u origin feature-branch
```

> -u in git push -u origin feature-branch:
> The -u flag is short for --set-upstream. When you use this flag, you're doing two things at once:
> 1. Pushing your local branch to the remote repository.
> 2. Setting up a tracking relationship between your local branch and the remote branch.

> After you've used -u once, you can simply use git push in the future for this branch, and Git will know which remote branch to push to.
> origin is the default name for the remote repository you cloned from.