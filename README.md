# OBS Studio Cursor skin
Selected source will  follow mouse pointer.
Using [`obs_sceneitem_set_pos`](https://obsproject.com/docs/reference-scenes.html#c.obs_sceneitem_set_pos) 
# Installation 
- Install pynput package from [pypi](https://pypi.org/project/pynput/) 
- Make sure your OBS Studio supports [scripting](https://obsproject.com/docs/scripting.html)
`python -m pip install pynput`
# Limitations
- Multiple monitors setup will not work .
- If used in fullscreen apps, offset will appear.
# Usage
- Create a _source_ with desired cursor(e.g Image source or Media source).
- In scripts select _that_ source name.
- Make a group, add Display Capture, Window Capture.

![img](https://i.imgur.com/CHuLwmp.png)

- To crop, crop the _group_, the size should still have the same ratio as your monitor even if you scale it
- To set offset/calibrate, use the Display Capture to see mouse and adjust it at Scripts (or use Tab/Shift+tab to navigate, if in Window Capture, to not move mouse). You have to do this every time you change the Group scale/move it

![img](https://user-images.githubusercontent.com/66927691/121442471-56133280-c9be-11eb-9bb4-ad12b2e4ebfb.jpg)

![img](https://user-images.githubusercontent.com/66927691/121442809-f23d3980-c9be-11eb-954f-c0e635e95d88.jpg)


- Test it: press Start, press Stop, tweak refresh rate.

# Web rendered mouse cursor trails
- Add browser source with mouse tracking local or online web page.
- Make sure to set resolution as your monitor (base)
- Fill all entries, check `Use browser source`

# Zoom
> Have you ever needed to zoom in on your screen to show some fine detail work,
> or to make your large 4k/ultrawide monitor less daunting?
> Zoom and Follow for OBS Studio does exactly that, zooms in on your mouse and follows it around.
> Configurable and low-impact, you can now do old school Camtasia zoom ins live

See: [Zoom and Follow](https://obsproject.com/forum/resources/zoom-and-follow.1051/) , [source code ](https://github.com/tryptech/obs-zoom-and-follow)

# Example cursors
They all have some level of transparency.
- yellow circle 
![img](https://i.imgur.com/ruzF9HN.png)
- red circle 
![img](https://i.imgur.com/8qoRU3i.png)
- green circle
![Imgur](https://i.imgur.com/s3jvZP5.png) 

# On the Roadmap
- Visual indicator of mouse up/down state.
- Lua based shaders rendering (on mouse up, down, trail, etc...)
- Custom web page rendering (on mouse up, down, trail, etc...)

# Acknowledgments
- [`3_4_700`](https://github.com/34700) added offsets functionality for precise custom cursor(like a hand drawn arm holding a pen for artists)
- [`tholman/cursor-effects`](https://github.com/tholman/cursor-effects) - stock cursor trails

# Contribute
 [Forks](https://help.github.com/articles/fork-a-repo) are a great way to contribute to a repository.
After forking a repository, you can send the original author a [pull request](https://help.github.com/articles/using-pull-requests)
