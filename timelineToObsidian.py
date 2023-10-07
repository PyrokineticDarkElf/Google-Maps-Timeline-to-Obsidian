import os
import json
import tempfile
import shutil  # Import the shutil module for file and directory cleanup
from datetime import datetime, timezone

# Constants
EMOJI_MAPPING = {
    'IN_PASSENGER_VEHICLE': '🚗',
    'IN_BUS': '🚌',
    'MOTORCYCLING': '🏍️',
    'STILL': '🧘‍♂️',
    'WALKING': '🚶‍♂️',
    'CYCLING': '🚴‍♂️',
    'FLYING': '✈️',
    'IN_TRAIN': '🚆',
    'IN_FERRY': '⛴️',
    'RUNNING': '🏃‍♂️',
    'IN_SUBWAY': '🚇',
    'IN_TRAM': '🚋',
    'SKIING': '⛷️',
    'SAILING': '⛵',
    'IN_VEHICLE': '🚗'
}

# Function to clean invalid characters from a filename
def clean_filename(filename):
    # Remove characters not allowed in Windows filenames
    invalid_chars = '\/:*?"<>|'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename

# Function to convert latitudeE7 and longitudeE7 values to standard format
def e7_to_standard(e7_value):
    return e7_value / 10**7
    
# Use the EMOJI_MAPPING constant to map activity types to emojis
def text_to_emoji(text):
    emoji = EMOJI_MAPPING.get(text, '❓')  # Using the EMOJI_MAPPING constant
    return emoji

# Function to convert a timestamp to 24-hour time format
def convert_to_24_hour_format(timestamp_str):
    # Parse the timestamp string to a datetime object
    timestamp = datetime.fromisoformat(timestamp_str)

    # Format the datetime object as a 24-hour time string
    time_str_24_hour = timestamp.strftime('%H:%M:%S')

    return time_str_24_hour

# Function to create a temporary directory
def create_temporary_directory():
    return tempfile.TemporaryDirectory(prefix="location_history_temp")

# Function to generate frontmatter
def generate_frontmatter(config, dir_name):
    if not config["output_frontmatter_toggle"]:
        return ""  # If frontmatter toggle is false, return an empty string

    frontmatter = "---\n"
    
    for key, value in config["output_frontmatter"].items():
        # If the key is "title," generate the title in the specified format using the dir_name
        if key == "title":
            # Convert the file name to a datetime object
            try:
                date_obj = datetime.strptime(dir_name.split('.')[0], '%Y-%m-%d')
                title_value = date_obj.strftime(config["output_frontmatter"]["title"]) # Use title to define title format
                frontmatter += f"{key}: {title_value}\n"
            except ValueError:
                # Skip directories that do not match the expected date format
                continue

        # If the key is "tags," generate the tags in the specified format
        if key == "tags":
            frontmatter += f"{key}:\n"
            for tag in value.split(","):
                frontmatter += f"  - {tag.strip()}\n"

    frontmatter += "---\n"

    return frontmatter

# Function to generate a Markdown table from a list of rows
def generate_markdown_table(h1, h2, b1, b2):
    # Create the header row
    header = f"|{h1}|{h2}|\n"
    separator = "| --- | --- |\n"
    body = f"|{b1}|{b2}|"

    # Combine the header, rows, and separator into a Markdown table
    table = header + separator + body + "\n"

    return table

# Function to split JSON data into day-specific folders
def split_json_data(input_folder, temp_folder):
    for root, _, files in os.walk(input_folder):
        for file_name in files:
            if file_name.endswith('.json'):
                input_file_path = os.path.join(root, file_name)

                with open(input_file_path, 'r', encoding='utf-8') as json_file:
                    data = json.load(json_file)
                    timeline_objects = data['timelineObjects']

                    for timeline_object in timeline_objects:
                        if 'activitySegment' in timeline_object:
                            # Check if it's an Activity Segment
                            segment = timeline_object['activitySegment']
                            start_timestamp = segment['duration']['startTimestamp']
                            date = datetime.fromisoformat(start_timestamp.split('.')[0])

                            # Create a new JSON file for each day
                            day_temp_folder = os.path.join(
                                temp_folder,
                                "Semantic Location History",
                                str(date.year),
                                date.strftime('%Y_%B'),
                                date.strftime('%Y-%m-%d')
                            )
                            os.makedirs(day_temp_folder, exist_ok=True)

                            temp_filename = clean_filename(f"{start_timestamp}_activity_segment.json")
                            temp_file_path = os.path.join(day_temp_folder, temp_filename)

                            with open(temp_file_path, 'w') as temp_file:
                                json.dump(timeline_object, temp_file, indent=4)

                        elif 'placeVisit' in timeline_object:
                            # Check if it's a Place Visit
                            visit = timeline_object['placeVisit']
                            start_timestamp = visit['duration']['startTimestamp']
                            date = datetime.fromisoformat(start_timestamp.split('.')[0])

                            # Create a new JSON file for each day
                            day_temp_folder = os.path.join(
                                temp_folder,
                                "Semantic Location History",
                                str(date.year),
                                date.strftime('%Y_%B'),
                                date.strftime('%Y-%m-%d')
                            )
                            os.makedirs(day_temp_folder, exist_ok=True)

                            temp_filename = clean_filename(f"{start_timestamp}_place_visit.json")
                            temp_file_path = os.path.join(day_temp_folder, temp_filename)

                            with open(temp_file_path, 'w') as temp_file:
                                json.dump(timeline_object, temp_file, indent=4)

# Function to merge JSON data into Markdown files
def merge_json_data(temp_folder, output_folder, iframe_base_url, main_folder_name, year_format, month_format, day_format):
    for root, dirs, _ in os.walk(temp_folder):
        for dir_name in dirs:
            day_folder = os.path.join(root, dir_name)
            day_files = [f for f in os.listdir(day_folder) if f.endswith('.json')]
            day_files.sort() # Sort files by name (which contains timestamps)

            markdown_content = generate_frontmatter(config, dir_name)

            for day_file in day_files:
                with open(os.path.join(day_folder, day_file), 'r', encoding='utf-8') as json_file:
                    data = json.load(json_file)

                    if 'activitySegment' in data and config['output_activity_segments']:
                        segment = data['activitySegment']

                        # Get Duration of visit
                        start_timestamp_str = segment['duration']['startTimestamp']
                        end_timestamp_str = segment['duration']['endTimestamp']
                        # Start and end time as string
                        start_time_24_hour = convert_to_24_hour_format(start_timestamp_str)
                        end_time_24_hour = convert_to_24_hour_format(end_timestamp_str)

                        # Combine start and end time in to output string
                        # Initialize the time_output as an empty string
                        time_output = ""
                        # Check and add start and end time based on switches
                        if config['output_activity_start_time_24_hour'] or config['output_activity_end_time_24_hour']:
                            if config['output_activity_start_time_24_hour']:
                                time_output += "⏳ " + start_time_24_hour
                            if config['output_activity_start_time_24_hour'] and config['output_activity_end_time_24_hour']:
                                time_output += " "
                            if config['output_activity_end_time_24_hour']:
                                time_output += "⌛ " + end_time_24_hour
                        else:
                            time_output = " "

                        # Parse the timestamps into datetime objects and make them timezone-aware (UTC)
                        start_timestamp = datetime.fromisoformat(start_timestamp_str.split('.')[0]).replace(tzinfo=timezone.utc)
                        end_timestamp = datetime.fromisoformat(end_timestamp_str.split('.')[0]).replace(tzinfo=timezone.utc)
                        # Calculate the duration
                        duration = end_timestamp - start_timestamp
                        # Extract hours and minutes from the duration
                        hours, remainder = divmod(duration.seconds, 3600)
                        minutes = remainder // 60

                        # Combine activity type emoji and formatted duration as string
                        # Initialize the type_and_duration as an empty string
                        type_and_duration = ""
                        # Check and add type_and_duration based on switches
                        if config['output_activity_activityType'] or config['output_activity_formatted_duration']:
                            # Get activity type
                            if 'activityType' in segment and config['output_activity_activityType']:
                                activity_type = segment['activityType']
                                type_and_duration += text_to_emoji(activity_type) # Convert to emoji
                            if config['output_activity_activityType'] and config['output_activity_formatted_duration']:
                                type_and_duration += " "
                            # Format the duration as a string if output is required
                            if config['output_activity_formatted_duration']:
                                if hours > 0:
                                    type_and_duration += f"{hours} hours and {minutes} minutes"
                                else:
                                    type_and_duration += f"{minutes} minutes"
                        else:
                            type_and_duration = " "

                        # Get start and end location
                        # Check if 'startLocation' exists and contains 'latitudeE7'
                        if 'startLocation' in segment and 'latitudeE7' in segment['startLocation']:
                            start_loc_lat = e7_to_standard(segment['startLocation']['latitudeE7'])
                            start_loc_long = e7_to_standard(segment['startLocation']['longitudeE7'])
                        if 'endLocation' in segment and 'latitudeE7' in segment['endLocation']:
                            end_loc_lat = e7_to_standard(segment['endLocation']['latitudeE7'])
                            end_loc_long = e7_to_standard(segment['endLocation']['longitudeE7'])

                        # Check and add iframe content based on switches
                        if config['output_activity_start_iframe'] or config['output_activity_end_iframe']:
                            if config['output_activity_start_iframe']:
                                iframe_start = f'<iframe src="{iframe_base_url.format(loc_lat=start_loc_lat, loc_long=start_loc_long)}"></iframe>'
                            else:
                                iframe_start = " "
                            if config['output_activity_end_iframe']:
                                iframe_end = f'<iframe src="{iframe_base_url.format(loc_lat=end_loc_lat, loc_long=end_loc_long)}"></iframe>'
                            else:
                                iframe_end = " "

                        # Add it to the markdown content
                        markdown_content += f"## Activity Segment\n"

                        # Make table rows based on switches
                        if (
                            config['output_activity_activityType']
                            or config['output_activity_formatted_duration']
                            or config['output_activity_start_time_24_hour']
                            or config['output_activity_start_iframe']
                            or config['output_activity_end_time_24_hour']
                            or config['output_activity_end_iframe']
                        ):

                            activity_segment_table = generate_markdown_table(
                                type_and_duration, time_output, iframe_start, iframe_end
                            )
                            # Add the generated table to the markdown content
                            markdown_content += activity_segment_table
                        
                        markdown_content += '\n'


                    if 'placeVisit' in data and config['output_place_visits']:
                        visit = data['placeVisit']
                        markdown_content += f"## 🗺️ Place Visit\n"

                        # Calculate Duration of visit
                        start_timestamp_str = visit['duration']['startTimestamp']
                        end_timestamp_str = visit['duration']['endTimestamp']
                        # Parse the timestamps into datetime objects and make them timezone-aware (UTC)
                        start_timestamp = datetime.fromisoformat(start_timestamp_str.split('.')[0]).replace(tzinfo=timezone.utc)
                        end_timestamp = datetime.fromisoformat(end_timestamp_str.split('.')[0]).replace(tzinfo=timezone.utc)
                        # Calculate the duration
                        duration = end_timestamp - start_timestamp
                        # Extract hours and minutes from the duration
                        hours, remainder = divmod(duration.seconds, 3600)
                        minutes = remainder // 60
                        # Format the duration as a string
                        if config['output_place_formatted_duration']:
                            if hours > 0:
                                formatted_duration = f"⏱️ {hours} hours and {minutes} minutes"
                            else:
                                formatted_duration = f"⏱️ {minutes} minutes"
                        else:
                            formatted_duration = " "

                        # Get location
                        # Check if 'location' exists and contains 'latitudeE7'
                        if 'location' in visit and 'latitudeE7' in visit['location']:
                            loc_lat = e7_to_standard(visit['location']['latitudeE7'])
                            loc_long = e7_to_standard(visit['location']['longitudeE7'])
                        # Start and end time
                        start_time_24_hour = convert_to_24_hour_format(start_timestamp_str)
                        end_time_24_hour = convert_to_24_hour_format(end_timestamp_str)


                        # Location name
                        if config['output_place_location']:
                            location_name = f"📌 {visit['location'].get('name', 'N/A')}"
                        else:
                            location_name = " "


                        # Format detailed data
                        if config['output_place_start_time_24_hour'] or config['output_place_end_time_24_hour'] or config['output_place_address'] or config['output_place_semanticType'] or config['output_place_place_id']:
                            # Combine start and end time in to output string
                            time_output = ""
                            # Check and add start and end time based on switches
                            if config['output_place_start_time_24_hour'] or config['output_place_end_time_24_hour']:
                                if config['output_place_start_time_24_hour']:
                                    time_output += "⏳ " + start_time_24_hour
                                if config['output_place_start_time_24_hour'] and config['output_place_end_time_24_hour']:
                                    time_output += " "
                                if config['output_place_end_time_24_hour']:
                                    time_output += "⌛ " + end_time_24_hour
                                if config['output_place_start_time_24_hour'] or config['output_place_end_time_24_hour']:
                                    time_output += "<br>"
                            else:
                                time_output = " "

                            # Get address
                            if config['output_place_address']:
                                address = visit['location'].get('address', 'N/A') + "<br>"
                            else:
                                address = ""

                            # Get semanticType
                            if config['output_place_semanticType']:
                                semantic_type = "Type: " + visit['location'].get('semanticType', 'N/A') + "<br>"
                            else:
                                semantic_type = ""

                            # Get place_id
                            if config['output_place_place_id']:
                                if 'location' in visit and 'placeId' in visit['location']:
                                    place_id = "🆔 " + visit['location']['placeId'] + "<br>"
                            else:
                                place_id = ""

                            detailed_data = time_output + address + semantic_type + place_id
                        else:
                            detailed_data = " "

                        # Check and add iframe content based on switches
                        if config['output_place_iframe']:
                            iframe_location = f"<iframe src='{iframe_base_url.format(loc_lat=loc_lat, loc_long=loc_long)}'></iframe>"
                        else:
                            iframe_location = " "


                        # Make table rows based on switches
                        if (
                            config['output_place_location']
                            or config['output_place_formatted_duration']
                            or config['output_place_iframe']
                            or config['output_place_start_time_24_hour']
                            or config['output_place_end_time_24_hour']
                            or config['output_place_address']
                            or config['output_place_semanticType']
                            or config['output_place_place_id']
                        ):

                            place_visit_table = generate_markdown_table(
                                location_name, formatted_duration, iframe_location, detailed_data
                            )
                            # Add the generated table to the markdown content
                            markdown_content += place_visit_table

                        markdown_content += '\n'


                # Write the merged content to a Markdown file
                if markdown_content:
                    # Convert the file name to a datetime object
                    try:
                        date_obj = datetime.strptime(dir_name.split('.')[0], '%Y-%m-%d')
                    except ValueError:
                        # Skip directories that do not match the expected date format
                        continue

                    year = date_obj.strftime(year_format) # Use year_format to define year folder name
                    month = date_obj.strftime(month_format) # Use month_format to define month folder name
                    day = date_obj.strftime(day_format) # Use day_format to define day folder name

                    # Create the subdirectories if they don't exist
                    subfolder = os.path.join(output_folder, main_folder_name, year, month)
                    os.makedirs(subfolder, exist_ok=True)

                    # Construct the full output file path
                    output_file_path = os.path.join(subfolder, day + ".md")
                    
                    with open(output_file_path, 'w', encoding='utf-8') as markdown_file:
                        markdown_file.write(markdown_content)


# Main function
def main():
    global config
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)

    # Extract folder structure options from the config
    input_folder = config["input_folder"]
    output_folder = config["output_folder_structure"]["output_folder"]
    main_folder_name = config["output_folder_structure"]["main_folder_name"]
    year_format = config["output_folder_structure"]["year_format"]
    month_format = config["output_folder_structure"]["month_format"]
    day_format = config["output_folder_structure"]["day_format"]
    # Extract iframe template from the config
    iframe_base_url = config["iframe_base_url"]

    # Initialize the temporary directory object
    temp_folder = None

    try:
        # Create a temporary directory
        temp_folder = create_temporary_directory()
        # Get the path of the temporary directory
        temp_folder_path = temp_folder.name
        # Split JSON data into temporary folders
        split_json_data(input_folder, temp_folder_path)
        # Merge JSON data into Markdown files
        merge_json_data(temp_folder_path, output_folder, iframe_base_url, main_folder_name, year_format, month_format, day_format)
    finally:
        # Ensure cleanup of the temporary directory
        if temp_folder:
            temp_folder.cleanup()

if __name__ == "__main__":
    main()
