from flask import Flask, render_template, request, redirect, url_for, send_file
from pytube import YouTube
import instaloader
import os

L = instaloader.Instaloader()

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        return redirect(url_for('preview', url=url))
    return render_template('index.html')

@app.route('/preview', methods=['POST'])
def preview():
    input_value = request.form['url']
    video_type=None
    if "instagram.com/" in input_value:
        post = instaloader.Post.from_shortcode(L.context, input_value.split("/")[-2])
        if post.is_video:
            return render_template('download_video.html', post=post)
        else:
            return render_template('download_photo.html', post=post)
    elif "youtu.be/" in input_value:
        url = request.form.get('url')
        resolution = request.form.get('resolution')
        video = YouTube(url)
        streams = video.streams.filter(file_extension='mp4')
        if resolution:
            streams = streams.filter(res=resolution)
            video_type = streams.filter(adaptive=True, only_video=True).first()
        if not video_type:
            video_type = streams.filter(adaptive=False, only_video=True).first()
            streams = streams.filter(adaptive=False, only_video=False, only_audio=False)
            resolutions = list(set([stream.resolution for stream in streams]))
            resolutions = sorted([r for r in resolutions if r is not None], reverse=True)
            return render_template('preview.html', video=video, video_type=video_type, resolutions=resolutions)               
    else:
        return redirect('/download_stories/' + input_value)

@app.route('/download_stories/<username>')
def download_stories(username):
    L = instaloader.Instaloader()
    user = "isk_513"
    passwd = "Isk@513"
    L.login(user, passwd)
    L.load_session_from_file(user)
    profile = instaloader.Profile.from_username(L.context, username)
    story_items = []
    for story in L.get_stories(userids=[profile.userid]):
        for item in story.get_items():
            L.download_storyitem(item, 'stories')
            story_items.append(item)
            print(f"Downloaded story from {item.owner_username}")
    return render_template('download_stories.html', username=username, story_items=story_items)   

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
