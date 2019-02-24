# PNGer
A PNG Parser, that doesn't barf on malformed/corrupted PNG files, but tells you about the structure of the file. It's aimed at forensic / anti-forensic purposes, and will not attempt to validate the bytes of the image, but just the format of the file. It also will not perform any rendering of the image. This is not the point/purpose of this tool.

# About
I wrote a basic version of this script in order to scrub data off of a PNG file. I had to write that when I couldn't find a tool to do it for me at a cursory glance (without uploading the PNG to some website, where who knows what that website owner does with your data/PNG then?). When I wrote that script, I realized, it might be of use to someone else. Also, I should make my script better. So I did that, and that is how PNGer was born!

# Features
## Validity Checks
Performs checks for the various PNG chunks to see if they are valid/properly formed or not. Amongst the checks, it will provide a list of the checks a given chunk passed/failed.

## PNG Chunk Ordering
Allows for the re-ordering of PNG chunks within the file, and also displays the order the chunks appear in the original file. Additionally, there are options for filtering certain chunks of the file through or not when passing through the script. See usage examples for more information on this.

## Low Memory Consumption (relative to it being a python script)
This is particularly useful for large PNG files. Basically, when reading the file through, I don't actually store the bytes of the image, which is generally going to be the largest parts of the file. When you do want to read those out, they are grabbed on the fly; python generators are nice for this type of thing, because who knows how big of a PNG file you're going to be looking at and wanting to manipulate!!

# Usage
To use at the command line, generally going to look like this:
```bash
$ ./main.py -i /path/to/input.png -o /path/to/output.png
```
I include main.py as an example for using the PNGParser class, but ultimately, it's a class that can be imported in whatever script you need it in.

Example in a script:
```python3
import png_parser

# TODO
# ...
# 
```

# TODO
I'll try to make GH issues for things that I want to build into this.. but it might not happen, it might just stay as TODOs in the code. I'm just working on this during my free time when I feel like it.

To name a few things I'd like to see though:
* Support for non-standard chunk names (e.g. Script crashes on undefined chunk names, fix this)
* Validity checks on chunk names (i.e. is the chunk name only upper/lower case ascii characters)
* Validity checks against specific chunks (e.g. is IDAT data well-formed?)
* Stego checks (i.e. is there any data in the file that is intended to be hidden? e.g. LSB stego)
* Validity explanations (e.g. This file is valid, e.g. This file is invalid because chunk 1 is not an IHDR chunk)

# License
MIT I suppose. Though, honestly, I'm not too stuck on that. If you have an actual opinion on the license of this software, please contact me about your concerns and we can work to sort it out.

# Contributing
Sure! Probably best if you open an issue or a PR against this repo and I can take a look at your bug/feature/code and we can see if we can work it in. :) Thanks for the help or use of my work, I'm glad it could be of use to someone other than me.
