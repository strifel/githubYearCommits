# Github Year Commits / Github Contribution Challenge
## About
<a href="https://github.com/robmroi03">Robmroi</a> and I asked ourselves who is more active on github since the beginning of the year.<br>
Because counting was needed when looking onto the github profile I made this to automatically count.

Since then (a year ago) this evolved a bit, and is now in a usable state and could be used for Contribution Overviews/Challenges.
A use case I can think of is at a Hackathon where you want to create (something like) a leaderboard.

This project is still being worked on:
### Todos:
- let the people edit their profile pages
- More types of challenges (not only year/eternity). Enter a specific start/end date.
- Make everything more beautiful (Please help! :))
## Installation
### Docker way:
`docker run --name gyc -p 8000:80 -d strifel:githubyearcommits`
### Manual way: 
1. clone the repo
2. run `python3 install.py` and enter a (new) password when prompted. (WARING: Do not use any standard password.)
3. Configure your web server (e.g. Apache WGSI, gunicorn) to use `app.py` (Or run `app.py` (not recommended)). ([ApacheWGSI Config](https://github.com/strifel/githubYearCommits/wiki/Apache-WGSI-Configuration))
4. Navigate your web browser to the page `/login`.
5. Enter admin as username and your new password and setup names of github account(/participants) (Important. only public contributions are count unless you show private contributions on your github account page)
6. Go to the main page (remove /admin in the address bar)
7. Go back to `/admin` and play with the settings ([User permissions informations](https://github.com/strifel/githubYearCommits/wiki/Permissions)).
## Update
#### Recommended only on releases!
1. Stop your web server.
2. Pull the repo (`git pull`)
3. Execute database script (`python3 update.py`)
4. Start your web server.
5. Check out new settings/functions.
## Notice
- You can force reload by going to `/force` path(can be disabled)
- Admin can force reload even if disabled
- You can click on count and hover over another to see percentage.
- You can change path to sqlite database by changing `GYC_DATABASE` environmental variable 
## Known issues
- Apache WGSI normally starts everytime a new instance. This will disable caching completely. (Disable that feature of WGSI to use caching)([See Apache WGSI Configuration](https://github.com/strifel/githubYearCommits/wiki/Apache-WGSI-Configuration))
## License
On 26th Juli 2018 this is on MIT License.
## Special Thanks go out to
- robmroi for the idea, the design and the darkmode
- sallar for giving an api for contributions
- All the people who build a library (I use).
- Stack Overflow Community (of course).
