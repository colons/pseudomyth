pseudomyth
==========

A script that parses filenames in a folder looking for videos with common
release filename structures and plays them back in an appropriately random
order.

Example
-------

::

   $ pip install pseudomyth

   $ ls
   [Coalgirls]_Clannad_10_(1280x720_Blu-Ray_FLAC)_[3827A783].mkv
   [Coalgirls]_Clannad_ED_(1280x720_Blu-Ray_FLAC)_[A230547E].mkv
   [Coalgirls]_Clannad_OP_(1280x720_Blu-Ray_FLAC)_[940FB269].mkv
   [Commie] Persona 4 - 25 [Director's Cut] [BD 720p AAC] [311CA781].mkv
   [Commie] Persona 4 - 26 [True Ending] [BD 720p AAC] [0A24880E].mkv
   [HorribleSubs] Space Brothers - 19 [720p].mkv
   [HorribleSubs] Space Brothers - 20 [720p].mkv
   [HorribleSubs] Space Brothers - 21 [720p].mkv
   [HorribleSubs] YuruYuri - 04 [720p].mkv
   [HorribleSubs] YuruYuri - 05 [720p].mkv
   [SGKK-Ruri] Deadman Wonderland - 01 (1280x720 H264 AAC) [666F0275].mkv
   [SGKK-Ruri] Deadman Wonderland - 02 (1280x720 H264 AAC) [CD79F07F].mkv

   $ pseudomyth 
   ／人◕ ‿‿ ◕人＼  ＬＥＴ’Ｓ　ＷＡＴＣＨ　１０　ＫＥＩＯＮＳ！
   Clannad [10] OP ED 
   Deadman Wonderland [1, 2] 
   Persona 4 [25, 26] 
   Space Brothers [19, 20, 21] 
   YuruYuri [4, 5] 

At this stage, if the list of episodes is to your satisfaction, you could hit
enter and pseudomyth would start playing back the first present episode of a
random series. Shows with more present episodes are more likely to be picked.
In the case of (in this example) Clannad, the opening and ending would be
played prior to and following the episode selected.

Once an episode has been played, it is moved to a 'consumed' subdirectory of
the current working directory and the cycle begins anew. You could, at this
point, either ^C out of the script or hit enter to watch another episode.
Because watched episodes are moved, you can stop and resume between episodes at
will.

Configuration
-------------

If you don't want to use your system's default video player or pseudomyth can't
work out what your system's default player is, you can configure an alternative
command in a ~/.pseudomyth file. The command is specified as a shell command,
where ``{filenames}`` will be replaced with the files (usually just one) to be
played back. For example, mine looks like this:

::

   [DEFAULT]
   command=mpv -fs {filenames}
