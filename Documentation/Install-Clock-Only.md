# Install Instructions for PiClock (Clock Only)

This version of the instructions is for setting up just the clock
itself, ignoring all the other options.   It also assumes you have
some OS already setup.   So this is useful for setting up the
clock on a desktop OS.

# Prerequisites

The minium requirements for a PiClock is pretty simple
* Python 3
* Python Qt5, known as PyQt5
* git (as an alternative to git, you can download the zip file from GitHub)

Theses are available under Windows, Linux, and OSX OS's.

How to get these installed on your choice of system I'll leave
as an exercise for the reader.

### Get the PiClock software
1. On GitHub.com, navigate to the main page of the repository: [PiClock](../)
2. Above the list of files, click the **< > Code** button.
3. Copy the HTTPS URL for the repository. It'll look something like this:
https://github.com/USERNAME/PiClock.git
4. Log into your Pi, (either on the screen or via ssh) (NOT as root).
You'll be in the home directory of the user pi (/home/pi) by default,
and this is where you want to be.  Note that the following command while
itself not being case-sensitive, further operation of PiClock may be
affected if the upper and lower case of the command is not followed.
5. Download PiClock using the `git clone` command followed by the 
HTTPS URL for the repository, for example:

```
git clone https://github.com/USERNAME/PiClock.git
```

Once that is done, you'll have a new directory called PiClock.

Alternatively, you can download the zip file from GitHub
by clicking the **< > Code** button above the list of files at [PiClock](../), 
select **Download ZIP**, then unzip it onto your system.

### Configure the PiClock API keys

You need to set API keys for one weather service and one map service.
These are free unless you have large volume.
The PiClock usage is well below the maximums imposed by the no cost API keys.

_Protect your API keys._  You'd be surprised how many pastebin's are out
there with valid API keys, because of people not being careful.   _If you post
your keys somewhere, your usage will skyrocket, and your bill as well._  Google
has the ability to add referer, device and IP requirements on your API key.  It
can also allow you to limit an API key to specific applications only (static-maps)
in this case. Also, you might consider disabling all the other APIs on your
project dashboard. Under the Billing section of things you can set up budgets
and alerts (set to like $1.00).

#### Weather API Key

You have your choice of OpenWeather or Tomorrow from which to get your 
current weather and forcast data.
You only need one or the other (owmapi or tmapi)

#### OpenWeather API key

An OpenWeather API key is required to use OpenWeather data.

OpenWeather API keys are created by signing up at this link:
https://openweathermap.org/price

Select either the One Call by Call API 3.0 subscription plan, or scroll down for the 
Professional Collections current weather and forecasts free plan.

The OpenWeather One Call by Call API 3.0 key requires a credit card which won't be charged 
unless usage is high. If you subscribe to the One Call API 3.0 plan, the default call limit is set 
to 2,000 API calls per day, however only the first 1,000 calls are free, which 
you should not exceed under typical PiClock operation.
After the daily limit is reached, the overage charge is $0.15 per 100 calls.
To be safe, it is recommended you change the daily limit by going to the 
"Billing plans" tab in your OpenWeather Personal account, and change the standard 
"Calls per day (no more than)" setting to 1,000 calls.

#### Tomorrow API key

A Tomorrow API key is required to use Tomorrow weather data.

Tomorrow API keys are created by signing up at this link:
https://www.tomorrow.io/weather-api/

#### Map API Key

You have your choice of Mapbox or Google Maps from which to get your underlying maps.
You only need one or the other (mbapi or googleapi)

#### Mapbox API key

A Mapbox API key (access token) is required to use Mapbox.

Mapbox access tokens are created by signing up at this link:
https://www.mapbox.com/signup/

#### Google Maps API key

A Google Maps API key is required to use Google Maps.
(Requires credit card which won't be charged unless usage is high.)

An intro to Google static maps API keys, and a link to creating your account and API keys:
https://developers.google.com/maps/documentation/maps-static/intro
You'll require a Google user and password.  It'll also require a credit card.
The credit card should not be charged, because my reading of
https://cloud.google.com/maps-platform/pricing/sheet/ the $200.00 credit will
apply, and your charges incurred will be for 31 map pulls per month will be
$0.62 , if you reboot daily.
You'll be required to create a "project" (maybe PiClock for a project name?)
You need to then activate the key.

Now that you have your API keys, copy the ApiKeys-example.py as ApiKeys.py and edit it...

```
cd PiClock/Clock
cp ApiKeys-example.py ApiKeys.py
nano ApiKeys.py
```
Put your API keys in the file as indicated. Comment out the lines of unused API keys.
```
# Change this to your API keys

# Map API keys -- only need 1 of the following
# Google Maps API key (if usemapbox is not set in Config)
googleapi = 'YOUR GOOGLE MAPS API KEY'
# Mapbox API key (access_token) [if usemapbox is set in Config]
mbapi = 'YOUR MAPBOX ACCESS TOKEN'

# Weather API key -- only need 1 of the following
# If you want to use OpenWeatherMap.org, uncomment and add API key
owmapi = 'YOUR OPENWEATHERMAP API KEY'
# If you want to use Tomorrow.io, uncomment and add API key
# tmapi = 'YOUR TOMORROW API KEY'
```

### Configure your PiClock
Here's where you tell PiClock where your weather should come from, and the
radar map centers and markers.  Copy the Config-Example.py as Config.py and edit it...

```
cd PiClock/Clock
cp Config-Example.py Config.py  (copy on windows)
[use your favorite editor] Config.py
```

This file is a python script, subject to python rules and syntax.
The configuration is a set of variables, objects and arrays,
set up in python syntax.  The positioning of the {} and () and ','
are not arbitrary.  If you're not familiar with python, use extra
care not to disturb the format while changing the data.

The first thing is to change the Latitudes and Longitudes you see to yours.
They occur in several places. The first one in the file is where your weather
forecast comes from.   The others are where your radar images are centered
and where the markers appear on those images.  Markers are those little red
location pointers.

### Run it!

```
cd PiClock
python3 PyQtPiClock.py
```
After a few seconds, your screen should be covered by the PiClock. YAY!

There may be some output on the terminal screen as it executes.
If everything works, it can be ignored.  If for some reason the clock
doesn't work, or maps are missing, etc. the output may give a reason
or reasons, which usually reference something to do with the config
file (Config.py)

### First Use

  * The space bar or right or left arrows will change the page.
  * F2 will start and stop the NOAA weather radio stream
  * F4 will close the clock


### Updating to newer/updated versions
Since you pulled the software from GitHub originally, it can be updated
using git and GitHub.
```
cd PiClock
git pull
bash update.sh
```
This will automatically update any part(s) of the software that has changed.
The update.sh script will then convert any config files as needed.
