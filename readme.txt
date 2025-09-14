1)Direct .yarn Reading: The script now opens and reads .yarn files line by line.

2)Syntax-Aware: It looks for title:, ---, and === to understand the structure of your nodes.

3)Parses Line IDs: It will automatically generate Line IDs if none is defined

4)Extracts Characters: It correctly identifies lines like CharacterName: Dialogue text... and separates the name from the text.

5)Handles Choices: It finds lines starting with ->, cleans them up, and puts them in the CSV.

6)File Discovery: The automatic file discovery searches for .yarn files