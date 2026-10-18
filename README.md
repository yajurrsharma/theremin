# Theremin

you must've heard of this instrument right? played without contact. and well, im making this instrument for my final physics project!

now i thought, why not create a web version of this too.. with your camera.. and so i went down the rabbit hole and oh boy, was this THE PROJECT :P

initially i had thought of making ONLY a theremin, hence the projects name, but then i thought why not add some flavour and some more interesting stuff, and well, here we are. presenting theremin, which is, NOT JUST a theremin, but a music sequencer!

## Installation

all the external files you need are already in their respective folders. all you need to do is download the required modules using:
```bash
pip install -r requirements.txt
```
then go to `main/instruments/` and run `sequencer.py`. it should start a flask server, running on `localhost:5000`. DO NOTE THAT THIS APPLICATION NEEDS YOUR WEBCAM PERMISSION TO RUN!

IF YOU'RE ON WINDOWS, the steps mentioned till here might not work, as windows does not come with a pre installed dll of FluidSynth. you'll have to install it via chocolatey:

```bash
choco install fluidsynth
```

## How to use (and how it works)

when the web interface opens, you'll see 5 buttons showing you different instruments on the screen, along with your camera.
clicking on the instruments one by one sets their order, in which they'll be prompted to be played on your camera. 

once you've chosen the order, click on "record" to start recording the first instrument! bring your right hand's index finger in the camera frame (AWAY FROM THE BOX!) and a red circle should appear on the tip. moving this circle inside the circle, or on its edge will play the instrument sound ONCE. 

make beats. go crazy. 

once you're done with the instrument, click the record button again to stop recording. you'll listen to your recorded piece play in the background. also note, that the length of your current recorded instrument will not necessarily match the length of your next recorded instrument, so it might play longer or shorter than it!

clicking the record button again starts the second instrument prompt, with the previous one playing in the background! so you can match and make beats! (do know that the looping and playing might be a little wacky, as i wasn't able to completely refine it :P)

if you're satisfied with the just 2, you can click on finalise and play and it'll play whatever was recorded till that instant, once. or, you could do all 5 and go wild :D


making this project took me around 8 and a half hours, over the span of almost a day and a half. this was made as a part of HackClub Expedition!
