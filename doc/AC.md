# AC - Automatic Coloring (Hinting)

## Background

AC was written by Bill Paxton. Originally, it
was integrated with the font editor, FE, but Bill extracted the
hinting code so it could run independently and would be easier to
maintain.

## Input

AC reads a glyph outline in bez format. The fontinfo
data is also read to get alignment zone information, the list of H,V counter
glyphs, the list of auxiliary H,V stem values, and whether or not flex
can be added to a glyph.

As the bez data is read a doubly linked-list is created that contains the
path element information, e.g. coordinates, path type (moveto, curveto...),
etc.

## Setup

The following initial setup and error checking is done after a glyph
is read:

1. Calculate the glyph bounding box to find the minimum and maximum
   x, y values. Supposedly, the very minimum hinting a glyph will get
   is its bounding box values.

2. Check for duplicate subpaths.

3. Check for consecutive movetos and only keep the last one.

4. Check that the path ends with a single closepath and that there are
   matching movetos and closepaths.

5. Initialize the value of the largest vertical and horizontal stem
   value allowed. The largest vertical stem value is the larger of 86.25
   and the largest value in the auxiliary V stem array. The largest
   horizontal stem value is the larger of 86.25 and the largest value in
   the auxiliary H stem array.

6. If flex is allowed add flex to the glyph. The current flex
   algorithm is very lax and flex can occur where you least expect it.
   Almost anything that conforms to page 72 of the black book is flexed.
   However, the last line on page 72 says the flex height must be 20 units
   or less and this should really say 10 units or less.

7. Check for smooth curves. If the direction arms tangent to the curve
   is between 0 and 30 degrees the points are forced to be colinear.

8. If there is a sharp angle, greater than 140 degrees, the angle will
   be blunted by adding another point. There’s a comment that says as of
   version 2.21 this blunting will not occur.

9. Count and save number of subpaths for each path element.

## Hinting

Generate possible hstem and vstem values. These values are saved as a
linked list (the coloring segment list) in the path element data structure.
There are four segment lists, one for top, bottom, left, and right segments.
The basic progression is: path → segments → values → hints, where a
segment is a horizontal or vertical feature, a value is a pair of
segments (top and bottom or left and right) that is assigned a priority
based on the length and width of a stem, and hints are non-overlapping
pairs with the highest priority.

### Generating {H,V}Stems

The path element is traversed and possible coordinates are added to the
segment list. The x or y coordinate is saved depending on if it’s a
top/bottom or left/right segment and the minimum and maximum extent for a
vertical or horizontal segment. These coordinates are included in the list:
a) the coordinates of horizontal/vertical lines, b) if this is a curve find the
bends (bend angle must be 135 degrees or less to be included);
don’t add a curve’s coordinate if the point is not at an extreme and is
going in the same direction as the previous path, c) add points at
extremes, d) add bands for s-curves or where an inflection point occurs,
e) checks are made to see if the curve is in a blue zone and a coordinate
added at the appropriate place.

Compact the coloring segment lists by removing any pairs that are
completely contained in another. Filter out bogus bend segments and
report any near misses to the horizontal alignment zones.

### Evaluating Stems

Form all top and bottom, left and right pairs from segment list and
generate ghost pairs for horizontal segments in alignment zones.
A priority value is assigned to each pair. The value is a function
of the length of the segments, the length of any overlap, and the
distance apart. A higher priority value means it is a likely candidate
to be included in the hints and this is given to pairs that are closer
together, longer in length, and have a clean overlap. All pairs with
0 priority are discarded.

Report any near misses (1 or 2 units) to the values in the H or V stems
array.

### Pruning Values

Prune non-relevant stem pairs and keep the best of any overlapping pairs.
This is done by looking at the priority values.

### Finding the Best Values

After pruning, the best pair is found for each top, bottom or left, right
segment using the priority values. Pairs that are at the same location
and are “similar” enough are merged by replacing the lower priority pair
with the higher priority pair.

The pairs are again checked for near misses (1 or 2 units) to the
values in the H or V stems array, but this time the information is
saved in an array. If fixing these pairs is allowed the pairs saved
in the array are changed to match the value it was “close” to in the
H or V stem array.

Check to see if H or V counter hints (hstem3, vstem3) should be used
instead of hstem or vstem.

Create the main hints that are included at the beginning of a glyph.
These are created by picking, in order of priority, from the segment
lists.

If no good hints are found use bounding box hints.

## Shuffling Subpaths

The glyph’s subpaths are reordered so that the hints will not need
to change constantly because it is jumping from one subpath to another.
Kanji glyphs had the most problems with this which caused huge
files to be created.

## Hint Substitution

Remove “flares” from the segment list. Flares usually occur at the top
of a serif where a hint is added at an endpoint, but it’s not at the
extreme and there is another endpoint very nearby. This causes a blip
at the top of the serif at low resolutions. Flares are not removed if
they are in an overshoot band.

Copy hints to earlier elements in the path, if possible, so hint
substitution can start sooner.

Don’t allow hint substitution at short elements, so remove any if
they exist. Short is considered less than 6 units.

Go through path element looking for pairs. If this pair is compatible
with the currently active hints then add it otherwise start hint
substitution.

## Special Cases

When generating stems a procedure is called to allow lines that are not
completely horizontal or vertical to be included in the coloring
segment list. This was specifically included because the serifs of
ITCGaramond Ultra have points that are not quite horizontal according
to the comment int the program. When generating hstem values the threshold
is ≤ 2 for delta y and ≥ 25 for delta x. The reverse is true when
generating vstem values.

There are many thresholds used when evaluating stems, pruning, and
finding the best values. The thresholds used throughout the program are
just “best guesses” according to Bill Paxton. There are various comments
in the code explaining why some of these thresholds were changed and
specifically for which fonts.

The following glyphs attempt to have H counter hints added.

> "element", "equivalence", "notelement", "divide"

in addition to any glyphs listed in the HCounterChars keyword of
the fontinfo file.

The following glyphs attempt to have V counter hints added.

> "m", "M", "T", "ellipsis"

in addition to any glyphs listed in the VCounterChars keyword of
the fontinfo file.

There used to be a special set of glyphs that received dotsection
hints. This was to handle hinting on older PS interpreters that could
not perform hint replacement. This feature has been commented out of
the current version of AC.

AC uses a 24.8 Fixed type number rather than the more widely used 16.16.

## Output

AC writes out glyphs bez format that includes
the hinting information. Along with each hint it writes a comment
that specifies which path element was used to create this hint.
This comment is used by BuildFont for hinting multiple master
fonts.

## Platforms

AC should run on Unix and Unix-like operating systems, Mac OS X and Microsoft
Windows, both 32-bit and 64-bit. The code is written in portable C.

AC consists of one header file and about 28 C files.
