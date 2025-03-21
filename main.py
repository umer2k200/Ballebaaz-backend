from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
import firebase_admin
import os
from firebase_admin import credentials, storage
from moviepy import VideoFileClip, concatenate_videoclips
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

# Initialize Firebase Admin SDK
cred = credentials.Certificate('ballebaaz-74803.json')
cred = credentials.Certificate({
    "type": os.getenv('FIREBASE_TYPE'),
    "project_id": os.getenv('FIREBASE_PROJECT_ID'),
    "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID'),
    "private_key": os.getenv('FIREBASE_PRIVATE_KEY').replace('\\n', '\n'),
    "client_email": os.getenv('FIREBASE_CLIENT_EMAIL'),
    "client_id": os.getenv('FIREBASE_CLIENT_ID'),
    "auth_uri": os.getenv('FIREBASE_AUTH_URI'),
    "token_uri": os.getenv('FIREBASE_TOKEN_URI'),
    "auth_provider_x509_cert_url": os.getenv('FIREBASE_AUTH_PROVIDER_CERT_URL'),
    "client_x509_cert_url": os.getenv('FIREBASE_CLIENT_CERT_URL')
})
firebase_admin.initialize_app(cred, {
    'storageBucket': 'ballebaaz-74803.appspot.com'
})

bucket = storage.bucket()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

import socket
hostname = socket.gethostname()
LOCAL_IP = socket.gethostbyname(hostname)

def download_clips_from_storage(folder_path, local_dir='clips'):
    """
    Downloads clips from the specified folder in Firebase Storage to a local directory.
    """
    if not os.path.exists(local_dir):
        os.makedirs(local_dir)

    blobs = bucket.list_blobs(prefix=folder_path)  # List all blobs in the folder
    clip_paths = []

    for blob in blobs:
        if blob.name.endswith('.mp4'):  # Only process .mp4 files
            local_path = os.path.join(local_dir, os.path.basename(blob.name))
            blob.download_to_filename(local_path)
            clip_paths.append(local_path)
            print(f'Downloaded {blob.name} to {local_path}')

    return clip_paths

def concatenate_clips(clip_paths, output_path='output.mp4'):
    """
    Concatenates video clips and saves the result locally.
    """
    clips = [VideoFileClip(path) for path in clip_paths]
    final_clip = concatenate_videoclips(clips)
    final_clip.write_videofile(output_path, codec='libx264')  # Save concatenated video locally
    print(f'Concatenated video saved locally at {output_path}')
    return output_path

def upload_to_storage(file_path, destination_path):
    """
    Uploads a local file to Firebase Storage.
    """
    blob = bucket.blob(destination_path)
    blob.upload_from_filename(file_path)
    print(f'Uploaded {file_path} to {destination_path}')


def delete_other_clips(folder_path):
    """
    Deletes all .mp4 files in the specified folder except 'concatenated_output.mp4'.
    """
    blobs = bucket.list_blobs(prefix=folder_path)  # List all blobs in the folder

    for blob in blobs:
        if blob.name.endswith('.mp4') and not blob.name.endswith('concatenated_output.mp4'):
            blob.delete()
            print(f'Deleted {blob.name}')

@app.route('/concatenate', methods=['POST'])
def concatenate_videos():
    data = request.json

    # Extract player_id, match_id, and type from the request payload
    id = data.get('id')
    match_id = data.get('match_id')
    clip_type = data.get('type')  # e.g., 'batting' or 'bowling'
    entity_type= data.get('entity_type')

    if not id or not match_id or not clip_type or not entity_type:
        return jsonify({"error": "player_id, match_id, and type, and entity_type are required "}), 400
 
    # Construct the folder path dynamically
    # folder_path = f'highlights/players/{player_id}/{match_id}/{clip_type}/'

    if entity_type == 'player':
        folder_path = f'highlights/players/{id}/{match_id}/{clip_type}/'
    elif entity_type == 'team':
        folder_path = f'highlights/teams/{id}/{match_id}/{clip_type}/'
    else:
        return jsonify({"error": "Invalid entity_type. Must be 'player' or 'team'."}), 400

    local_dir = data.get('local_dir', 'clips')
    output_path = data.get('output_path', 'concatenated_output.mp4')

    # Step 1: Download clips from Firebase Storage
    clip_paths = download_clips_from_storage(folder_path, local_dir)

    if not clip_paths:
        return jsonify({"error": "No clips found to concatenate."}), 404

    # Step 2: Concatenate clips and save locally
    concatenated_clip_path = concatenate_clips(clip_paths, output_path)

    # Step 3: Upload concatenated clip back to Firebase Storage
    upload_to_storage(concatenated_clip_path, f'{folder_path}concatenated_output.mp4')

    # Step 4: Delete other clips in the folder
    delete_other_clips(folder_path)

    return jsonify({
        "message": "Videos concatenated and uploaded successfully.",
        "output_path": concatenated_clip_path,
        "folder_path": folder_path
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5001)))  # Run on port 5001









# from flask import Flask, request, jsonify
# import firebase_admin
# import os
# from firebase_admin import credentials, storage
# from moviepy import VideoFileClip, concatenate_videoclips

# # Initialize Firebase Admin SDK
# cred = credentials.Certificate('D:\\STUDY\\Highlights\\ballebaaz.json')
# firebase_admin.initialize_app(cred, {
#     'storageBucket': 'ballebaaz-74803.appspot.com'
# })

# bucket = storage.bucket()

# app = Flask(__name__)

# def download_clips_from_storage(folder_path, local_dir='clips'):
#     """
#     Downloads clips from the specified folder in Firebase Storage to a local directory.
#     """
#     if not os.path.exists(local_dir):
#         os.makedirs(local_dir)

#     blobs = bucket.list_blobs(prefix=folder_path)  # List all blobs in the folder
#     clip_paths = []

#     for blob in blobs:
#         if blob.name.endswith('.mp4'):  # Only process .mp4 files
#             local_path = os.path.join(local_dir, os.path.basename(blob.name))
#             blob.download_to_filename(local_path)
#             clip_paths.append(local_path)
#             print(f'Downloaded {blob.name} to {local_path}')

#     return clip_paths

# def concatenate_clips(clip_paths, output_path='output.mp4'):
#     """
#     Concatenates video clips and saves the result locally.
#     """
#     clips = [VideoFileClip(path) for path in clip_paths]
#     final_clip = concatenate_videoclips(clips)
#     final_clip.write_videofile(output_path, codec='libx264')  # Save concatenated video locally
#     print(f'Concatenated video saved locally at {output_path}')
#     return output_path

# def upload_to_storage(file_path, destination_path):
#     """
#     Uploads a local file to Firebase Storage.
#     """
#     blob = bucket.blob(destination_path)
#     blob.upload_from_filename(file_path)
#     print(f'Uploaded {file_path} to {destination_path}')

# @app.route('/concatenate', methods=['POST'])
# def concatenate_videos():
#     data = request.json
#     folder_path = data.get('highlights/players/P227/M002/batting/')
#     local_dir = data.get('local_dir', 'clips')
#     output_path = data.get('output_path', 'concatenated_output.mp4')

#     if not folder_path:
#         return jsonify({"error": "folder_path is required"}), 400

#     # Step 1: Download clips from Firebase Storage
#     clip_paths = download_clips_from_storage(folder_path, local_dir)

#     if not clip_paths:
#         return jsonify({"error": "No clips found to concatenate."}), 404

#     # Step 2: Concatenate clips and save locally
#     concatenated_clip_path = concatenate_clips(clip_paths, output_path)

#     # Step 3: Upload concatenated clip back to Firebase Storage
#     # upload_to_storage(concatenated_clip_path, f'{folder_path}concatenated_output.mp4')

#     return jsonify({"message": "Videos concatenated and uploaded successfully.", "output_path": concatenated_clip_path}), 200

# if __name__ == '__main__':
#     app.run(debug=True, port=5001)  # Run on port 5001