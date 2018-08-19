# Github Year Commit
## Why?
<a href="https://github.com/robmroi03">Robmroi</a> and I asked ourselves who is more active on github since the beginning of the year.<br>
Because counting is needed when looking onto the github profile I made this to automatically count.
## Installation
1. clone the repo
2. run `python3 databaseCreate.py` and enter a password when prompted.
3. run `python3 app.py` (or use your flask webserver (even better)).
4. Get the ip address of your device and navigate with a browser to: `your_ip_address:5000/login`
5. Enter your password and setup names of github account (!Important only public contributions are count unless you show private contributions on your github account page)
6. Go to the main page (remove /login or /backend in the address bar)
7. enjoy
## Useful
You can change cache duration in database.
You can click on count and hover over another to see percentage.
## License
On 26th Juli 2018 this is on MIT License.
## Special Thanks
go out to robmroi for the idea, sallar for giving an api for contributions.
And to all people who build a library (I use).