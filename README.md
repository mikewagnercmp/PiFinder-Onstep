# PiFinder
 A plate solving telescope finder based around a Raspberry PI, RPI HQ Camera, and custom UI 'hat'
![Banner](./images/banner_overview.png)

I'm a visual observer using a 16" f4.5 dobsonian.   The lightweight/low-eyepiece design of my scope is great for transport and use... but it also means there is no great way to add reliable encoders to get solid scope positioning.

After seeing some people succeed building small plate-solving systems for feeding telescope position information to a laptop or tablet... I decided to try to build something similar, but with it's own user-interface rather than relying on a tablet or other device.  Thus the PiFinder was born!

The PiFinder is my attempt to improve my time at my telescope.  I don't get nearly enough of it and I want to enjoy it as much as possible.  So after years of observing with paper charts and, later, a Nexus DSC here is what I felt I was missing:
* **Reliable telescope positioning:**  The Nexus DSC is great, but my scope just isn't built for solid encoder integration.  The slop in the way I have to couple the encoders means poor pointing accuracy.
* **Easy setup:**  The Nexus DSC needs multi-star alignment to understand how the encoders map to the sky.  The process is not terrible, but I'd like to avoid it.
* **Good push-to functionality**:  This is one place the Nexus DSC shines... if it's well aligned.  The catalog system is okay, and once you select and object the screen is clear and helpful to get the telescope pointed correctly.
* **Observation logging**:  I like to keep track of what I see each night.  I don't often sketch, just record what I saw when, with what eyepiece and some basic info about the experience.  If I could do this right at the eyepiece, that'd save time.

My hope is that other people will find this combination of functionality useful, will build their own PiFinder and help the whole project improve by making suggestions and potentially contributing to the software.  It's a pretty easy build with off the shelf parts and beginner friendly soldering.  

## Features
* Zero setup: Just turn it on and point it at the sky!  
* Accurate pointing: Onboard GPS determines location and time while the camera determines where the scope is pointing.  Inertial Measurement Unit tracks scope motion and updates sky position between camera solves
* Self-contained:  Includes catalog search/filtering, sky/object charting, push-to guidance and logging all via the screen and keypad on the unit.
* Dark site friendly:  Red Oled screen has wide brightness adjustment, right down to 'off'. No need for bright cell phones or tablets
* Easy access: Can be mounted by the eyepiece just like a finder.

![PiFinder on my Dob](./images/PiFinder_on_scope.jpg)

If you'd like to learn more about how it works, and potentially build your own, everything you need should be here.  I recommend starting with the [User Manual](./docs/user_guide.md) and then checking out the build process using the links below.

## Docs

* [User Manual](./docs/user_guide.md)
* [Parts List](./docs/BOM.md) 
* [Build Guide](./docs/build_guide.md)
* [Software Setup](./docs/software.md)
* [Developer Guide](./docs/dev_guide.md)


<a href='https://ko-fi.com/brickbots' target='_blank'><img height='35' style='border:0px;height:46px;' src='https://az743702.vo.msecnd.net/cdn/kofi3.png?v=0' border='0' alt='Buy Me a Coffee at ko-fi.com' />
