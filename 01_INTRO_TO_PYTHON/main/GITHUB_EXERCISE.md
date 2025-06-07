## Github Exercise 

1. Create a GitHub Repository named `{nick_name}_mew_tutor_ai`
2. Clone the repository to your local machine
3. Create 4 folders (Exercise_1, ..., Exercise_4 each having an empty README.md).
**Git Basics**
```
git add .
git commit -m "chore: initial setup with 4 exercise folders"
git push origin main
```
4. Push the folders to github directly in the main branch.
5. **Branch**Create a new branch using `git checkout -b feature/exercise_1`
6. Make changes (e.g., add content to Exercise_1/README.md). Then execute the following
```
git add .
git commit -m "feat: add instructions to Exercise_1 README"
git push origin feature/exercise_1
```
7. Go to GitHub Interface and navigate to `Pull Request`. Open a pull request with a description such as `please merge my pull request I have added some changes to README in exercise` and assign yourself.
8. Click on merge branch. Then to sync your local development do
```
git checkout main
git pull origin main
```
9. Create an Issue, e.g. Please add `title` to Readme in Exercise 2 and self-assign.