# YuzuSCN

YuzuSCN is a library for creating and editing decompiled SCN data files from Yuzusoft visual novels, aimed at being a reliable and easy-to-use tool for modders.

The project is currently working in progress, and the API is not yet stable. However, it is functional and can be used to create and edit SCN files.

## Why this library?

I found that the existing projects for SCN editing all aim to translate original game content, but what I want to do is to create new content. However, if you look into the JSON of a decompiled SCN file, you will find that it is very complex and not easy to understand. Therefore, I decided to create this library to make it easier for modders to work with SCN files.

## Usage

For now temporarily, you can edit the SCN files through following steps:
1. Install the library using `pip install yuzuscn`.
2. Decompile the SCN file using PsbDecompile from [FreeMote](https://github.com/UlyssesWu/FreeMote).
3. Write a script to load the SCN file, modify it, and save it back.
    
    ```python
    from yuzuscn.models import Scn

    with open("example.scn.json", "r", encoding="utf-8") as f:
        scn = Scn.model_validate(f.read())
    
    # Modify the scn object as needed
    # For example, change the first line's text to "Hello, World!"
    scn.scenes[0].texts[0].dialogues[0].content = "Hello, World!"
    scn.scenes[0].texts[0].dialogues[0].length = len("Hello, World!")

    # Save the modified scn object back to a file
    with open("example_modified.scn.json", "w", encoding="utf-8") as f:
        f.write(scn.model_dump_json())
    ```
4. Compile the SCN file using PsBuild from FreeMote.
5. Test the modified SCN file in the game.

## Disclaimer

This library is not affiliated with Yuzusoft or any of its games. It is for personal and non-commercial use only. All Yuzusoft games content remains the property of their respective owners. Use this library at your own risk. The author is not responsible for any damage or loss caused by the use of this library.