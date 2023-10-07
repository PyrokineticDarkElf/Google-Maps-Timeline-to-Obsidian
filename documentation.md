# Documentation of functions in timelineToObsidian.py

## clean_filename(filename)
Description: This function takes a filename as input and removes characters that are not allowed in Windows filenames (such as /, \, :, *, ?, ", <, > and |).
Parameters: filename (str) - The input filename.
Returns: A cleaned filename with invalid characters replaced by underscores.

## e7_to_standard(e7_value)
Description: This function converts latitudeE7 and longitudeE7 values, which are in a format with seven decimal places, to standard latitude and longitude format.
Parameters: e7_value (int) - The latitudeE7 or longitudeE7 value.
Returns: The latitude or longitude value in standard format.

## text_to_emoji(text)
Description: This function maps activity types to emojis using the EMOJI_MAPPING constant.
Parameters: text (str) - The activity type text.
Returns: The corresponding emoji for the given activity type or '❓' if no mapping is found.

## convert_to_24_hour_format(timestamp_str)
Description: This function converts a timestamp string to a 24-hour time format.
Parameters: timestamp_str (str) - The timestamp string in ISO format.
Returns: The timestamp string in 24-hour time format (HH:MM:SS).

## create_temporary_directory()
Description: This function creates a temporary directory using Python's tempfile.TemporaryDirectory and returns the temporary directory object.
Parameters: None.
Returns: A temporary directory object.

## generate_markdown_table(h1, h2, b1, b2)
Description: This function generates a Markdown table with two header cells (h1 and h2) and two body cells (b1 and b2).
Parameters:
h1 (str) - The content for the first header cell.
h2 (str) - The content for the second header cell.
b1 (str) - The content for the first body cell.
b2 (str) - The content for the second body cell.
Returns: A Markdown table string.

## split_json_data(input_folder, temp_folder)
Description: This function splits JSON data into day-specific folders within a temporary directory based on the start timestamp of activities or place visits. This is important because Google provides JSON files containing a whole month's worth of data.
Parameters:
input_folder (str) - The folder containing JSON data to be split.
temp_folder (str) - The temporary directory where the data will be split into day-specific folders.
Returns: None.

## merge_json_data(temp_folder, output_folder, iframe_base_url, main_folder_name, year_format, month_format, day_format)
Description: This function merges JSON data into Markdown files, organized in a folder structure based on the provided parameters. It also formats the data and generates Markdown tables for activities and place visits.
Parameters:
temp_folder (str) - The temporary directory containing the split JSON data.
output_folder (str) - The root output folder where the Markdown files will be created.
iframe_base_url (str) - The base URL used to generate iframes for location data.
main_folder_name (str) - The name of the main folder within the output structure.
year_format (str) - The format for the year folder name.
month_format (str) - The format for the month folder name.
day_format (str) - The format for the day folder name.
Returns: None.

## main()
Description: The main function of the script. It reads configuration data from a JSON file, creates a temporary directory, splits and merges JSON data, and generates Markdown files.
Parameters: None.
Returns: None.

## NOTES
The script also includes a global variable config to store configuration data loaded from a JSON file and a constant EMOJI_MAPPING that maps activity types to emojis.
